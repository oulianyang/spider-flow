# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Identity

- **Name**: spider-flow v0.5.0
- **Type**: Visual web scraping platform (drag-and-drop flow editor, no code required)
- **Stack**: Java 8 · Spring Boot 2.0.7 · MyBatis-Plus 3.1.0 · MySQL · FastJSON 1.2.83 · Jsoup · mxGraph
- **Entry class**: `org.spiderflow.SpiderApplication`
- **Port**: 8088

---

## Rules — 必须遵守

### DO ✅

- 所有 `ShapeExecutor` / `FunctionExecutor` / `FunctionExtension` 实现类**必须**加 `@Component`
- `FunctionExecutor` 的 public static 方法**必须**加 `@Comment("说明")` 注解
- 读取节点属性**必须**用 `node.getStringJsonValue(key)`（自动 HTML 反转义）
- Mapper **必须**继承 `BaseMapper<T>`，Service **必须**继承 `IService<T>` 或 `ServiceImpl<M, T>`
- 新增节点类型时，`supportShape()` 返回值**必须**与前端 XML 中的 `shape` 字段完全一致
- Controller 接口**优先**返回 `JsonBean<T>` 作为统一响应

### DON'T ❌

- **不要**直接操作 `SpiderNode.jsonProperty` Map，使用 `getStringJsonValue()` / `getListJsonValue()`
- **不要**在 `spider-flow-api` 中引入业务依赖（Spring、数据库等），保持纯接口层
- **不要**使用 `${...}` 以外的表达式语法，引擎不支持其他模板格式
- **不要**修改 `SpiderContext.running` 为 true（只能从 true → false 用于中止任务）
- **不要**在 `ShapeExecutor.execute()` 中捕获并吞掉所有异常，异常会存入 `variables["ex"]` 供条件流转使用
- **不要**在前端 JS 中调用 `/rest/*` 接口，这些是外部系统专用
- **不要**同时设置 `allowedOrigins("*")` 和 `allowCredentials(true)`，违反 W3C CORS 规范，Spring 5.3+ 会抛异常

---

## Build & Run Commands

```bash
# 编译打包（产物: spider-flow-web/target/spider-flow.jar）
mvn clean package -DskipTests

# 启动
java -jar spider-flow-web/target/spider-flow.jar

# 访问（浏览器打开）
http://localhost:8088
```

---

## Module Navigation

依赖链：`spider-flow-web` → `spider-flow-core` → `spider-flow-api`

| 模块 | 职责 | 修改场景 |
|------|------|----------|
| `spider-flow-api/` | 接口契约层：扩展点接口、公共模型、上下文 | 新增扩展点接口、修改 SpiderNode/SpiderContext |
| `spider-flow-core/` | 业务实现层：爬虫引擎、执行器、表达式引擎、Service | 新增节点类型、新增表达式函数、修改引擎逻辑 |
| `spider-flow-web/` | Web 层：Controller、WebSocket、前端静态资源 | 新增 API 接口、修改前端界面 |

> 每个模块目录下均有独立的 `CLAUDE.md`，进入模块修改代码前请先阅读对应文档。

---

## Core Execution Flow

```
正式执行（/rest/run, /spider/run, 定时任务）:
    HTTP 请求 / Quartz 调度
        ↓
    Spider.run(spiderFlow, context, variables)

测试/调试执行（WebSocket /ws）:
    WebSocket {"eventType":"test"/"debug"}
        ↓
    Spider.runWithTest(root, context)           测试模式入口，不写日志文件

两者共同路径:
    SpiderFlowUtils.loadXMLFromString(xml)      解析 mxGraph XML → SpiderNode 树
        ↓
    executeRoot(root, context, variables)       创建 SubThreadPoolExecutor
        ↓
    executeNode(fromNode, node, variables)      递归执行节点
        ↓
    ExecutorsUtils.get(shape)                   shape → ShapeExecutor 映射查找
        ↓
    executor.execute(node, context, variables)  执行节点逻辑
        ↓
    executeNextNodes(node, context, variables)  触发下级节点
```

**核心类速查：**

| 类 | 位置 | 说明 |
|----|------|------|
| `Spider` | `core/Spider.java` | 引擎主类：节点调度、线程池、死循环检测。`run()` 为正式执行，`runWithTest()` 为测试/调试执行 |
| `SpiderNode` | `api/model/SpiderNode.java` | 流程节点：JSON 属性、上下级、条件、原子计数器 |
| `SpiderContext` | `api/context/SpiderContext.java` | 执行上下文（extends HashMap）：线程池、FutureQueue、running 标志 |
| `ExecutorsUtils` | `core/utils/ExecutorsUtils.java` | ShapeExecutor 注册中心，`get(shape)` 查找执行器 |
| `ExpressionUtils` | `core/utils/ExpressionUtils.java` | 表达式执行入口，`execute(expr, variables)` |

---

## Extension Points（扩展点）

所有扩展通过 Spring DI 自动注册，实现接口 + `@Component` 即可。

### ShapeExecutor — 新增节点类型

```java
@Component
public class MyShapeExecutor implements ShapeExecutor {
    @Override
    public String supportShape() { return "myShape"; }  // 与前端 XML 中 shape 字段一致

    @Override
    public void execute(SpiderNode node, SpiderContext context, Map<String, Object> variables) {
        // 节点执行逻辑
    }

    @Override
    public Shape shape() {
        return new Shape("myShape", "节点名称", "icon-class"); // 前端工具栏展示，null 则隐藏
    }

    // 可选：执行完毕后是否允许继续执行下级节点（默认 true）
    @Override
    public boolean allowExecuteNext(SpiderNode node, SpiderContext context, Map<String, Object> variables) {
        return true;
    }

    // 可选：是否在线程池中异步运行（默认 true）；返回 false 则在当前线程同步执行
    @Override
    public boolean isThread() { return true; }
}
```

已有实现：`StartExecutor` / `RequestExecutor`（Grammerable + SpiderListener）/ `VariableExecutor`（`isThread()=false`，同步执行）/ `LoopExecutor` / `OutputExecutor`（SpiderListener）/ `ForkJoinExecutor` / `ExecuteSQLExecutor`（Grammerable）/ `ProcessExecutor` / `FunctionExecutor` / `CommentExecutor`

### FunctionExecutor — 新增表达式函数

```java
@Component
public class MyFunctionExecutor implements FunctionExecutor {
    @Override
    public String getFunctionPrefix() { return "myfunc"; } // 调用方式：myfunc.xxx()

    @Comment("将字符串转为大写")
    @Example("myfunc.upper('hello')")
    public static String upper(String str) { return str.toUpperCase(); }
}
```

> ⚠️ 所有 public static 方法**必须**加 `@Comment` 注解，否则前端代码提示中不会显示该函数。

### FunctionExtension — 为已有类型追加方法

```java
@Component
public class MyExtension implements FunctionExtension {
    @Override
    public Class<?> support() { return String.class; } // 扩展 String 类型

    @Comment("根据正则表达式提取内容")
    @Return({String.class})
    public static String regx(String source, String pattern) { /* ... */ }
    // 调用方式（第一个参数 source 自动为调用对象）：${strVar.regx('<title>(.*?)</title>')}
}
```

### SpiderListener — 生命周期监听

```java
@Component
public class MyListener implements SpiderListener {
    public void beforeStart(SpiderContext context) { /* 任务开始前 */ }
    public void afterEnd(SpiderContext context)    { /* 任务结束后 */ }
}
```

### Grammerable — 语法提示提供者

```java
@Component
public class MyExecutor implements ShapeExecutor, Grammerable {
    @Override
    public List<Grammer> grammers() {
        // 返回变量的语法提示列表，前端代码补全使用
        // 例如 RequestExecutor 返回 resp.html / resp.json / resp.statusCode 等
    }
}
```

> 实现该接口后，`/spider/grammers` 接口会自动收集提示数据，前端编辑器中输入变量名 `.` 时触发补全。

---

## Expression Syntax

表达式语法 `${...}`，由 `DefaultExpressionEngine` 解析执行。

```
${resp.html}                           访问变量属性
${extract.selector(html, '.title')}    调用 FunctionExecutor 函数
${"hello".upper()}                     调用 FunctionExtension 扩展方法
${i + 1}                               运算
${fetchCount == null ? 0 : fetchCount + 1}  三元表达式
```

执行入口：`ExpressionUtils.execute(expression, variables)`

---

## REST API

> **HTTP 方法说明**：除 `/spider/recent5TriggerTime`（`@GetMapping`，仅 GET）外，所有端点均使用 `@RequestMapping`（无方法限制，接受所有 HTTP 方法）。

### 前端接口 `/spider/*`（SpiderFlowController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/spider/list` | `page, limit, name` | 分页查询爬虫列表 |
| `/spider/save` | `SpiderFlow` 对象 | 保存/更新流程（同时写历史版本），返回裸 String 流程 ID（⚠️ 未包装 JsonBean，与其他接口不同） |
| `/spider/get` | `id` | 获取流程详情 |
| `/spider/remove` | `id` | 删除流程（含通知配置） |
| `/spider/start` | `id` | 启动定时任务（注册到 Quartz） |
| `/spider/stop` | `id` | 停止定时任务 |
| `/spider/run` | `id` | 立即执行一次 |
| `/spider/log` | `id, taskId, keywords, index, count, reversed, matchcase, regx` | 读取执行日志 |
| `/spider/log/download` | `id, taskId` | 下载日志文件 |
| `/spider/shapes` | — | 所有节点形状（前端工具栏） |
| `/spider/grammers` | — | 表达式语法提示（前端代码补全） |
| `/spider/pluginConfigs` | — | 已安装插件列表 |
| `/spider/recent5TriggerTime` | `cron` | 预览 Cron 最近5次触发时间（**仅 GET**） |
| `/spider/history` | `id, timestamp` | 查询历史版本列表或指定版本 |
| `/spider/other` | `id` | 获取其他流程列表，供子流程选择 |
| `/spider/copy` | `id` | 复制流程 |
| `/spider/cron` | `id, cron` | 修改 Cron 表达式 |
| `/spider/xml` | `id` | 获取原始 XML |

### 外部接口 `/rest/*`（SpiderRestController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/rest/run/{id}` | JSON body 可选参数 | 同步执行，返回 `JsonBean<List<SpiderOutput>>` |
| `/rest/runAsync/{id}` | — | 异步执行，返回 `JsonBean<Integer>`（taskId） |
| `/rest/status/{taskId}` | — | 查询任务状态（1=运行中，0=已结束/不存在） |
| `/rest/stop/{taskId}` | — | 停止任务 |

> ⚠️ `/rest/*` 是外部系统专用接口，前端页面**不要**调用。

### 数据源接口 `/datasource/*`（DataSourceController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/datasource/list` | `page, limit` | 分页查询数据源列表 |
| `/datasource/all` | — | 获取全部数据源（下拉选择用） |
| `/datasource/save` | `DataSource` 对象 | 保存/更新数据源 |
| `/datasource/get` | `id` | 获取单个数据源详情 |
| `/datasource/remove` | `id` | 删除数据源 |
| `/datasource/test` | `DataSource` 对象 | 测试数据源连接 |

### 函数接口 `/function/*`（FunctionController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/function/list` | `page, limit, name` | 分页查询自定义函数列表（`name` 可选筛选） |
| `/function/save` | `Function` 对象 | 保存/更新函数 |
| `/function/get` | `id` | 获取函数详情 |
| `/function/remove` | `id` | 删除函数 |

### 变量接口 `/variable/*`（VariableController，继承 CURDController）

> **CURDController 说明**：仅 `VariableController` 继承了 `CURDController` 基类，其他 Controller 各自实现 CRUD 方法。`CURDController.save()` 返回 `JsonBean<Boolean>`，`CURDController.get()` 返回 `JsonBean<T>`，与 SpiderFlowController 等的返回格式不同。

| 路径 | 参数 | 说明 |
|------|------|------|
| `/variable/list` | — | 变量列表 |
| `/variable/get` | `id` | 获取变量 |
| `/variable/save` | `Variable` 对象 | 保存/更新变量 |
| `/variable/delete` | `id` | 删除变量 |

### 任务接口 `/task/*`（TaskController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/task/list` | `flowId` | 查询任务执行记录 |
| `/task/stop` | `id` | 停止运行中的任务 |
| `/task/remove` | `id` | 删除任务记录 |

### 通知接口 `/flowNotice/*`（FlowNoticeController）

| 路径 | 参数 | 说明 |
|------|------|------|
| `/flowNotice/save` | `FlowNotice` 对象 | 保存/更新通知配置 |
| `/flowNotice/find` | `id` | 查询流程的通知配置 |
| `/flowNotice/getNoticeWay` | — | 获取可用通知方式列表 |

**WebSocket**：`/ws` 端点，推送测试执行日志和输出数据。

**CORS**：`ResourcesConfiguration` 已全局启用跨域（`allowedOrigins=*`，方法 `GET/POST/OPTIONS`，`allowCredentials=true`）。
> ⚠️ `allowedOrigins("*")` + `allowCredentials(true)` 违反 W3C CORS 规范，Spring WebMvc 5.3+ 会抛异常。当前 Spring Boot 2.0.7 恰好不校验，但升级后需修改。

---

## Database

执行 `db/spiderflow.sql` 初始化。主要表：

| 表 | 说明 |
|----|------|
| `sp_flow` | 爬虫流程（XML、Cron、启用状态） |
| `sp_datasource` | 数据源配置 |
| `sp_function` | 自定义函数 |
| `sp_variable` | 全局变量 |
| `sp_task` | 任务执行记录 |
| `sp_flow_notice` | 通知配置 |

---

## Common Tasks

| 任务 | 步骤 |
|------|------|
| 新增节点类型 | ① `core/executor/shape/` 新建 `XxxExecutor implements ShapeExecutor` ② 前端 `editor.html` 添加图形元素 |
| 新增表达式函数 | ① `core/executor/function/` 新建 `XxxFunctionExecutor implements FunctionExecutor` ② 所有方法加 `@Comment` |
| 新增类型扩展方法 | `core/executor/function/extension/` 新建 `XxxFunctionExtension implements FunctionExtension` |
| 新增 REST 接口 | 在 `web/controller/` 新建 Controller，返回 `JsonBean<T>` |
| 修改前端界面 | 直接编辑 `web/src/main/resources/static/` 下的 HTML/JS/CSS，重启服务生效，无需编译 |
| 新增数据源类型 | 修改 `core/utils/DataSourceUtils.java` + `core/executor/shape/ExecuteSQLExecutor.java` |

---

## Key Configuration

文件：`spider-flow-web/src/main/resources/application.properties`

```properties
# === 服务配置 ===
server.port=8088
logging.level.root=INFO
spring.mvc.favicon.enabled=false

# === 数据源（必需）===
spring.datasource.driver-class-name=com.mysql.jdbc.Driver
spring.datasource.username=root
spring.datasource.password=<你的MySQL密码>
spring.datasource.url=jdbc:mysql://localhost:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true

# === 爬虫引擎配置 ===
spider.thread.max=64               # 平台全局最大线程数
spider.thread.default=8            # 单任务默认线程数
spider.job.enable=true             # 定时任务总开关（设为 false 可禁用所有定时任务）
spider.workspace=/data/spider      # 日志和历史版本工作空间
spider.bloomfilter.capacity=1000000  # 布隆过滤器容量（RequestExecutor URL去重）
spider.bloomfilter.error-rate=0.0001 # 布隆过滤器容错率
#spider.detect.dead-cycle=5000      # 死循环检测阈值（仅测试模式有效，节点执行次数超过该值时终止）

# === Jackson 序列化 ===
spring.jackson.date-format=yyyy-MM-dd HH:mm:ss
spring.jackson.time-zone=GMT+8
spring.jackson.serialization.fail_on_empty_beans=false

# === 邮件通知（可选，通知功能必需）===
spring.mail.protocol=smtp
spring.mail.host=smtp.qq.com
spring.mail.port=465
spring.mail.username=<发件邮箱>
spring.mail.password=<邮箱授权码>
spring.mail.default-encoding=UTF-8
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true
spring.mail.properties.mail.smtp.starttls.required=true
spring.mail.properties.mail.smtp.socketFactory.class=javax.net.ssl.SSLSocketFactory
spring.mail.properties.mail.smtp.socketFactory.port=465
spring.mail.properties.mail.smtp.socketFactory.fallback=false

# === 通知内容模板（支持变量: {name}, {currentDate}）===
spider.notice.subject=spider-flow流程通知
spider.notice.content.start=流程开始执行：{name}，开始时间：{currentDate}
spider.notice.content.end=流程执行完毕：{name}，结束时间：{currentDate}
spider.notice.content.exception=流程发生异常：{name}，异常时间：{currentDate}

# === Selenium 插件（可选，需要时取消注释）===
selenium.driver.chrome=E:/driver/chromedriver.exe
selenium.driver.firefox=E:/driver/geckodriver.exe

# === 自动配置排除 ===
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration,org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration
```

> ⚠️ **BloomFilter 默认值说明**：`RequestExecutor` 代码中 `@Value` 注解的默认值为 `capacity=5000000` / `error-rate=0.00001`，但 `application.properties` 配置的值会覆盖代码默认值。实际生效值以 `application.properties` 为准。

---

## Plugin Modules

父 POM `dependencyManagement` 中声明了以下插件模块（需单独引入依赖才生效）：

| 插件 | 说明 |
|------|------|
| `spider-flow-selenium` | Selenium 浏览器自动化 |
| `spider-flow-proxypool` | 代理池 |
| `spider-flow-mongodb` | MongoDB 存储 |
| `spider-flow-redis` | Redis 缓存 |
| `spider-flow-ocr` | OCR 识别 |
| `spider-flow-oss` | OSS 对象存储 |
| `spider-flow-mailbox` | 邮箱收发 |

> 插件通过实现 `PluginConfig` 接口 + `@Component` 注册，前端 `/spider/pluginConfigs` 接口可查询已安装插件。

---

## Frontend

前端为**传统静态页面**（无 npm/webpack），位于 `spider-flow-web/src/main/resources/static/`：
- **UI 框架**：Layui + jQuery EasyUI
- **图形编辑**：mxGraph（`editor.html` 是核心编辑器）
- **代码编辑**：CodeMirror
- 修改后重启服务即可生效

---

## Docker Deployment

```bash
# 1. 编译
mvn clean package -DskipTests

# 2. 构建镜像
docker build -t spider-flow:latest .

# 3. 配置环境变量
cp .env.example .env   # 编辑 .env 设置 MYSQL_ROOT_PASSWORD 等

# 4. 启动（含 MySQL 8.0 + 应用）
docker compose up -d

# 5. 访问
http://localhost:8088
```

> `docker-compose.yml` 中 MySQL 使用 `mysql_native_password` 插件兼容项目内置的 MySQL Connector/J 5.x 驱动。Chrome for Testing 已内置在镜像中（Selenium 插件可用）。爬虫日志通过 `spider-workspace` 卷持久化到 `/data/spider`。
