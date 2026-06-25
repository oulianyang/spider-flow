# CLAUDE.md — spider-flow-web

## Module Identity

`spider-flow-web` 是项目的**Web 接入层与前端界面**，依赖 `spider-flow-core`。

负责：Spring Boot 启动、REST API、WebSocket 实时通信、静态前端资源托管。

---

## Rules for This Module

### DO ✅
- Controller 接口**优先**返回 `JsonBean<T>` 作为统一响应
- WebSocket 事件**必须**通过 `WebSocketEvent<T>` 封装推送
- `SpiderWebSocketContext` 覆写 `addOutput` / `pause` / `resume` / `stop` 实现实时推送
- 新增接口路径与现有风格保持一致（`/模块名/操作名`）

### DON'T ❌
- **不要**修改 `SpiderApplication` 的 `@MapperScan` 包路径，除非清楚影响范围
- **不要**在 `/rest/*` 接口中抛出未捕获异常，需返回 `JsonBean` 包装错误信息
- **不要**将 WebSocket 文本缓冲区改小，否则长日志会被截断
- **不要**在静态资源目录下放 Java 文件，也不要在 Java 目录下放 HTML/JS
- **不要**修改 `WebSocketConfiguration` 中 `Spider` 注入 `WebSocketEditorServer` 的方式（通过静态字段 + `@Autowired` setter）
- **不要**在 `WebSocketEditorServer.onClose()` 中省略 `context` 的 null 检查（当前代码未检查，若连接在未执行前关闭会触发 NPE）

---

## Directory Map

```
spider-flow-web/
├── src/main/java/org/spiderflow/
│   ├── SpiderApplication.java         # ★ Spring Boot 启动入口
│   ├── configuration/
│   │   ├── ResourcesConfiguration.java    # 静态资源映射
│   │   └── WebSocketConfiguration.java    # ServerEndpointExporter 注册
│   ├── controller/
│   │   ├── SpiderFlowController.java      # /spider/* 爬虫流程管理
│   │   ├── SpiderRestController.java      # /rest/*   外部系统调用
│   │   ├── DataSourceController.java      # 数据源管理
│   │   ├── FunctionController.java        # 自定义函数管理
│   │   ├── VariableController.java        # 全局变量管理
│   │   ├── TaskController.java            # 任务记录查询
│   │   └── FlowNoticeController.java      # 通知配置
│   ├── logback/
│   │   ├── SpiderFlowFileAppender.java    # Logback 文件追加器（日志写入文件）
│   │   └── SpiderFlowWebSocketAppender.java # Logback → WebSocket 推送
│   ├── model/
│   │   ├── SpiderWebSocketContext.java    # WebSocket 上下文（推送日志/输出）
│   │   └── WebSocketEvent.java            # WebSocket 消息结构
│   └── websocket/
│       └── WebSocketEditorServer.java     # ★ /ws 端点（测试/调试流程）
├── src/main/resources/
│   ├── application.properties             # 主配置文件
│   ├── logback-spring.xml                 # 日志配置
│   └── static/                            # 前端静态资源（无构建工具）
│       ├── index.html                     # 首页
│       ├── editor.html                    # ★ mxGraph 可视化编辑器
│       ├── spiderList.html                # 爬虫列表
│       ├── log.html                       # 日志查看
│       ├── datasources.html / datasource-edit.html
│       ├── functions.html / function-edit.html
│       ├── variables.html / variable-edit.html
│       ├── task.html / editCron.html / spiderList-notice.html
│       └── js/
│           ├── editor.js                  # ★ 编辑器主逻辑（48KB，最大文件）
│           ├── spider-editor.js           # 编辑器封装
│           ├── canvas-viewer.js           # 画布视图
│           ├── log-viewer.js              # 日志查看器
│           ├── common.js                  # 公共工具函数
│           ├── index.js                   # 首页逻辑
│           ├── mxgraph/                   # mxGraph 图形库
│           ├── codemirror/                # CodeMirror 代码编辑器
│           ├── layui/                     # Layui UI 框架
│           ├── cron/                      # Cron 编辑器组件
│           └── jsontree/                  # JSON 树形展示
```

---

## REST API — 详细接口说明

### `/spider/*` — 前端接口

| 路径 | 参数 | 说明 |
|------|------|------|
| `GET/POST /spider/list` | `page, limit, name` | 分页查询流程列表 |
| `POST /spider/save` | `SpiderFlow` 对象 | 保存/更新流程，同时写历史版本文件，返回裸 String 流程 ID（⚠️ 未包装 JsonBean） |
| `GET /spider/get` | `id` | 获取单个流程详情 |
| `POST /spider/remove` | `id` | 删除流程（含通知配置） |
| `POST /spider/start` | `id` | 启动定时任务（注册到 Quartz） |
| `POST /spider/stop` | `id` | 停止定时任务 |
| `POST /spider/run` | `id` | 立即执行一次 |
| `POST /spider/copy` | `id` | 复制流程 |
| `POST /spider/cron` | `id, cron` | 修改 Cron 表达式 |
| `GET /spider/xml` | `id` | 获取原始 XML |
| `GET /spider/log` | `id, taskId, keywords, index, count, reversed, matchcase, regx` | 读取执行日志 |
| `GET /spider/log/download` | `id, taskId` | 下载日志文件 |
| `GET /spider/shapes` | — | 所有节点形状（前端工具栏） |
| `GET /spider/grammers` | — | 表达式语法提示（前端代码补全） |
| `GET /spider/pluginConfigs` | — | 已安装插件列表 |
| `GET /spider/recent5TriggerTime` | `cron` | 预览 Cron 最近 5 次触发时间 |
| `GET /spider/history` | `id, timestamp` | 查询历史版本列表或指定版本 |
| `GET /spider/other` | `id` | 获取其他流程列表（子流程选择用） |

### `/rest/*` — 外部系统接口

| 路径 | 参数 | 说明 |
|------|------|------|
| `POST /rest/run/{id}` | JSON body 可选参数 | 同步执行，等待结果返回 |
| `POST /rest/runAsync/{id}` | — | 异步执行，立即返回 taskId |
| `GET /rest/status/{taskId}` | — | 查询异步任务是否仍在运行 |
| `POST /rest/stop/{taskId}` | — | 停止异步任务 |

> ⚠️ `/rest/*` 是外部系统专用接口，前端页面**不要**调用。

---

## WebSocket — `/ws` 端点

`WebSocketEditorServer` 处理前端编辑器的实时测试请求。

| 前端事件 | 行为 |
|----------|------|
| `{"eventType": "test", "message": "<xml>"}` | 创建 SpiderWebSocketContext，调用 `Spider.runWithTest()` 异步执行流程，推送日志和输出 |
| `{"eventType": "debug", "message": "<xml>"}` | 同 test，启用调试模式（支持断点暂停，通过 `context.pause()` 触发） |
| `{"eventType": "stop"}` | `context.running = false` + `context.stop()`，停止执行 |
| `{"eventType": "resume"}` | 恢复暂停的调试流程 |

> WebSocket 连接关闭时（`@OnClose`）也会自动将 `running` 设为 false 并调用 `stop()`。⚠️ 注意：当前代码未对 `context` 做 null 检查，若连接在未执行测试前关闭会触发 NPE。

**SpiderWebSocketContext 注意事项：**
- 覆写了 `addOutput` / `pause` / `resume` / `stop` 实现 WebSocket 实时推送
- **未覆写** `getOutputs()`（继承基类返回 `Collections.emptyList()`），因为 WebSocket 模式下输出通过 `addOutput` 实时推送，不需要汇总

**后端推送消息格式**（`WebSocketEvent<T>`）：
```json
{"eventType": "log|output|finish|error|debug", "message": ...}
```

> `debug` 事件类型在断点暂停时推送，包含 `{nodeId, event, key, value}` 信息，前端据此显示调试状态。

---

## SpiderApplication 启动配置

```java
@SpringBootApplication
@EnableScheduling                          // 定时任务支持
@MapperScan("org.spiderflow.*.mapper")     // MyBatis Mapper 扫描
public class SpiderApplication implements ServletContextInitializer {
    // 注册 PaginationInterceptor（MyBatis-Plus 分页）
    // onStartup() 中设置 WebSocket 文本缓冲区 = 1MB（防止长日志截断）
}
```

---

## Frontend Technology Stack

前端为**传统静态页面**，无 npm / webpack / Vite 等构建工具：

| 技术 | 用途 |
|------|------|
| Layui | UI 框架（表格、表单、弹窗） |
| mxGraph | 流程可视化编辑（节点拖拽、连线） |
| CodeMirror | 代码/表达式编辑器（语法高亮） |
| jQuery EasyUI | 部分页面 UI 组件（文件：`jquery.easyui.min.js`） |

> 修改前端代码后**只需重启服务**，无需编译前端。

---

## Configuration Classes

### ResourcesConfiguration

- 注册静态资源映射：`/static/**` → `classpath:/static/`
- 全局启用 CORS：`allowedOrigins=*`，允许 `GET/POST/OPTIONS`，`allowCredentials=true`
- ⚠️ `allowedOrigins("*")` + `allowCredentials(true)` 违反 W3C CORS 规范，Spring WebMvc 5.3+ 会抛异常。当前 Spring Boot 2.0.7 恰好不校验，但升级后需修改

### WebSocketConfiguration

- 注册 `ServerEndpointExporter` Bean，支持 `@ServerEndpoint` 注解
- 通过 `@Autowired` 将 `Spider` 实例注入到 `WebSocketEditorServer` 静态字段

