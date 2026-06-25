# CLAUDE.md — spider-flow-core

## Module Identity

`spider-flow-core` 是项目的**业务实现层**，依赖 `spider-flow-api`。

包含：爬虫引擎、节点执行器、表达式引擎、数据持久化、定时任务、业务服务。

---

## Rules for This Module

### DO ✅
- 所有 `ShapeExecutor` 实现类**必须**加 `@Component`，`supportShape()` 返回值必须与前端 XML 中 shape 字段完全一致
- 新增 `FunctionExecutor` 的 public static 方法**必须**加 `@Comment("说明")` 注解
- Mapper **必须**继承 `BaseMapper<T>`，Service **必须**继承 `ServiceImpl<Mapper, Entity>`
- 读取节点属性**必须**用 `node.getStringJsonValue(key)`，不直接操作 jsonProperty
- 节点异常存入 `variables["ex"]`，让条件箭头处理流转，而不是抛异常中断流程

### DON'T ❌
- **不要**在 `execute()` 中捕获所有异常而不处理，异常需存入 `variables["ex"]` 供条件判断
- **不要**直接调用 `Spider.run()` 执行流程，应通过 `SpiderJobManager` 或 Controller 接口
- **不要**修改 `ExecutorsUtils.executorMap` 的实现，Spring 自动注入所有 ShapeExecutor
- **不要**在 `SpiderFlowService` 中直接操作 Quartz，统一通过 `SpiderJobManager`

---

## Directory Map

```
spider-flow-core/src/main/java/org/spiderflow/core/
├── Spider.java                    # ★ 爬虫引擎主类
├── executor/
│   ├── shape/                     # 节点形状执行器（实现 ShapeExecutor）
│   │   ├── StartExecutor.java     #   shape="start"      流程起点，无实际逻辑
│   │   ├── RequestExecutor.java   #   shape="request"    HTTP 请求（最复杂，18KB）
│   │   ├── VariableExecutor.java  #   shape="variable"   定义/赋值变量
│   │   ├── LoopExecutor.java      #   shape="loop"       循环控制
│   │   ├── OutputExecutor.java    #   shape="output"     输出结果数据
│   │   ├── ForkJoinExecutor.java  #   shape="forkJoin"   分支汇聚（等待所有上游完成）
│   │   ├── ExecuteSQLExecutor.java#   shape="executeSql" 执行 SQL
│   │   ├── ProcessExecutor.java   #   shape="process"    子流程调用
│   │   ├── FunctionExecutor.java  #   shape="function"   执行自定义函数
│   │   └── CommentExecutor.java   #   shape="comment"    注释节点，无逻辑
│   └── function/                  # 表达式函数（实现 FunctionExecutor）
│       ├── StringFunctionExecutor.java    # 前缀: string
│       ├── ExtractFunctionExecutor.java   # 前缀: extract（CSS/XPath/JSONPath/正则）
│       ├── JsonFunctionExecutor.java      # 前缀: json
│       ├── DateFunctionExecutor.java      # 前缀: date
│       ├── Base64FunctionExecutor.java    # 前缀: base64
│       ├── MD5FunctionExecutor.java       # 前缀: md5
│       ├── UrlFunctionExecutor.java       # 前缀: url
│       ├── FileFunctionExecutor.java      # 前缀: file
│       ├── ListFunctionExecutor.java      # 前缀: list
│       ├── RandomFunctionExecutor.java    # 前缀: random
│       ├── ThreadFunctionExecutor.java    # 前缀: thread
│       └── extension/                     # 类型扩展（实现 FunctionExtension）
│           ├── StringFunctionExtension.java
│           ├── ResponseFunctionExtension.java
│           ├── ElementFunctionExtension.java    # Jsoup Element
│           ├── ElementsFunctionExtension.java   # Jsoup Elements
│           ├── ListFunctionExtension.java
│           ├── ArrayFunctionExtension.java
│           ├── MapFunctionExtension.java
│           ├── DateFunctionExtension.java
│           ├── ObjectFunctionExtension.java
│           └── SqlRowSetExtension.java
├── expression/                    # 自定义表达式引擎
│   ├── DefaultExpressionEngine.java       # 引擎实现
│   ├── ExpressionTemplate.java            # ${...} 模板处理
│   ├── ExpressionTemplateContext.java     # 变量+函数注册上下文
│   ├── ExpressionGlobalVariables.java     # 全局变量注入
│   ├── ExpressionError.java               # 错误处理
│   ├── interpreter/                       # AST 解释器
│   └── parsing/                           # 词法/语法解析
├── io/
│   ├── HttpRequest.java           # HTTP 请求（基于 JDK HttpURLConnection）
│   └── HttpResponse.java          # HTTP 响应（实现 SpiderResponse 接口）
├── job/                           # Quartz 定时任务
│   ├── SpiderJob.java             # 定时任务执行逻辑
│   ├── SpiderJobContext.java      # 定时任务上下文（写日志文件，create() 第四参数 output 控制是否收集输出）
│   └── SpiderJobManager.java      # 任务调度管理（addJob/remove/run）
├── mapper/                        # MyBatis-Plus Mapper
│   ├── SpiderFlowMapper.java
│   ├── DataSourceMapper.java
│   ├── FunctionMapper.java
│   ├── VariableMapper.java
│   ├── TaskMapper.java
│   └── FlowNoticeMapper.java
├── model/                         # 数据库实体
│   ├── SpiderFlow.java            # 爬虫流程（id/name/xml/cron/enabled）
│   ├── DataSource.java
│   ├── Function.java
│   ├── Variable.java
│   ├── Task.java
│   └── FlowNotice.java
├── script/
│   └── ScriptManager.java         # 动态脚本执行（自定义函数用）
├── serializer/
│   └── FastJsonSerializer.java    # FastJSON 序列化配置
├── service/                       # 业务服务层
│   ├── SpiderFlowService.java     # 流程 CRUD、定时任务、历史版本
│   ├── DataSourceService.java
│   ├── FunctionService.java
│   ├── VariableService.java
│   ├── TaskService.java
│   └── FlowNoticeService.java
└── utils/
    ├── SpiderFlowUtils.java       # XML 解析：mxGraph XML → SpiderNode 树
    ├── ExecutorsUtils.java        # ShapeExecutor 注册中心（shape → executor）
    ├── ExpressionUtils.java       # 表达式执行工具
    ├── DataSourceUtils.java       # 动态数据源管理
    ├── ExtractUtils.java          # 提取工具（CSS/XPath/正则）
    ├── FileUtils.java
    └── EmailUtils.java
```

---

## Spider Engine — 执行流程详解

```
Spider.run(SpiderFlow, context, variables)
    │
    ├── SpiderFlowUtils.loadXMLFromString(xml)   解析 mxGraph XML → SpiderNode 树
    ├── flowNoticeService.sendFlowNotice(start)  发送开始通知
    │
    └── executeRoot(root, context, variables)
            │
            ├── 创建 SubThreadPoolExecutor（节点 threadCount，+1 用于调度）
            ├── 选择 ThreadSubmitStrategy（random/linked/child/parent）
            ├── listeners.beforeStart(context)
            │
            └── 提交根任务 → executeNode(null, root, ...)
                    │
                    ├── executeCondition(fromNode, node, vars)  判断箭头条件
                    ├── ExecutorsUtils.get(shape)               查找执行器
                    ├── 解析 loopCount（数组/数字）             计算循环次数
                    │
                    └── 循环创建 SpiderTask 提交到线程池
                            │
                            └── executor.execute(node, context, vars)
                                    ↓ 任务完成后
                                task.node.decrement()              计数器减一
                                executor.allowExecuteNext(...)     检查是否允许继续
                                executeNextNodes(node, ...)        触发下级节点
```

### 关键配置项

| 配置键 | 默认值 | 说明 |
|--------|--------|------|
| `spider.thread.max` | 64 | 全局最大线程数 |
| `spider.thread.default` | 8 | 单任务默认线程数 |
| `spider.detect.dead-cycle` | 5000 | 死循环检测阈值（仅测试模式有效） |
| `spider.bloomfilter.capacity` | 1000000 | 布隆过滤器容量（RequestExecutor URL去重，代码 @Value 默认 5000000，以 application.properties 为准） |
| `spider.bloomfilter.error-rate` | 0.0001 | 布隆过滤器容错率（代码 @Value 默认 0.00001，以 application.properties 为准） |

### 异常流转机制

- 节点执行异常时，异常存入 `variables["ex"]`，**不会中断整个流程**
- 箭头可配置异常流转：`exception="1"` 表示有异常时走这条线，`"2"` 表示无异常时走
- **不要**在 `execute()` 中捕获并吞掉所有异常，异常需要传递给条件判断逻辑

---

## Shape Executors — 节点执行器详解

### RequestExecutor（最复杂）

- 实现接口：`ShapeExecutor` + `Grammerable` + `SpiderListener`
- `Grammerable`：提供 `resp` 变量的前端代码提示
- `SpiderListener`：在 `afterEnd` 中持久化 BloomFilter 到磁盘
- 方法：GET / POST / PUT / DELETE
- 请求体：none / raw / form-data（支持文件上传）
- 支持代理、重定向控制、TLS 验证、超时设置、重试（retryCount/retryInterval）
- 自动管理 Cookie（通过 `CookieContext`，可通过 `cookie-auto-set` 控制）
- 支持 URL 去重（基于 BloomFilter，通过 `repeat-enable` 开启）
- 支持延迟请求（`sleep` 属性，支持表达式）
- 调试断点支持（通过 `context.pause()` 实现）
- **响应仅在 statusCode=200 时存入变量 `resp`**，后续节点可用：

| 属性 | 说明 | 示例 |
|------|------|------|
| `resp.html` | 响应文本 | `${resp.html}` |
| `resp.json` | JSON 解析结果 | `${resp.json}` |
| `resp.statusCode` | HTTP 状态码 | `${resp.statusCode}` |
| `resp.title` | 网页标题 | `${resp.title}` |
| `resp.cookies` | 响应 Cookies | `${resp.cookies}` |
| `resp.headers` | 响应 Headers | `${resp.headers}` |
| `resp.bytes` | 响应字节数组 | `${resp.bytes}` |
| `resp.contentType` | Content-Type | `${resp.contentType}` |
| `resp.url` | 当前 URL | `${resp.url}` |
| `resp.stream` | 响应 InputStream | `${resp.stream}` |

  > 另外可通过 `StringFunctionExtension` 在 `resp.html` 上调用 `selector()`、`xpath()`、`regx()`、`jsonpath()` 等扩展方法。

### VariableExecutor

- `isThread()` 返回 `false`，在当前线程**同步执行**（非阻塞操作，无需线程池）
- `execute()` 实际执行变量赋值逻辑（将节点属性值通过表达式求值后存入 variables）

### LoopExecutor

- `execute()` 为空实现，**不覆写** `allowExecuteNext()`（默认返回 true）
- 循环逻辑实际在 `Spider.executeNode()` 中实现：解析节点 `loopCount` 属性（支持数组/数字），循环创建 SpiderTask 提交到线程池
- 循环下标变量名由 `loopVariableName` 指定
- 循环 item 变量名由 `loopItem` 指定（默认 `item`），常量 `LoopExecutor.LOOP_ITEM`
- `loopStart` / `loopEnd` 控制循环范围（支持负数表示末尾偏移），常量 `LoopExecutor.LOOP_START` / `LoopExecutor.LOOP_END`

### ForkJoinExecutor

- `execute()` 为空实现，主要逻辑在 `allowExecuteNext()` 中
- 检查当前节点是否 `isDone()`（递归检查本节点及所有祖先节点的计数器是否归零），未全部完成返回 `false`
- 未完成的分支变量会被缓存到内部 `cachedVariables` Map，当所有分支完成后合并到当前变量中传递给下级
- 用于多条分支汇聚时等待所有分支完成

### ProcessExecutor

- 执行子流程：读取 `flowId` 属性，从数据库获取另一个 SpiderFlow 的 XML，调用 `spider.executeNode(null, root, context, variables)` 执行（注意不是 `Spider.run()`，而是直接执行根节点）

---

## Expression Engine — 表达式引擎

语法 `${...}`，引擎实现位于 `expression/` 目录。

| 用法 | 示例 |
|------|------|
| 变量属性访问 | `${resp.html}` |
| Map 下标访问 | `${variables["key"]}` |
| FunctionExecutor 函数 | `${extract.selector(html, '.title')}` |
| FunctionExtension 扩展方法 | `${resp.selector('.title')}`（第一个参数自动为调用对象） |
| 算术运算 | `${i + 1}` |
| 三元表达式 | `${fetchCount == null ? 0 : fetchCount + 1}` |

执行入口：`ExpressionUtils.execute(expression, variables)`

---

## Scheduled Jobs（定时任务）

- `SpiderJobManager` 管理 Quartz Scheduler，提供 `addJob(flow)` / `remove(id)` / `run(id)`
- `SpiderFlowService.initJobs()` 启动时扫描 `enabled=1` 的任务，自动注册到 Quartz
- 日志写入路径：`{workspace}/{flowId}/logs/{taskId}.log`
- 历史版本路径：`{workspace}/{flowId}/xmls/{timestamp}.xml`

---

## FunctionExecutor 函数前缀速查

| 类 | 前缀 | 核心方法示例 |
|---|---|---|
| `StringFunctionExecutor` | `string` | `lowercase()`, `uppercase()`, `trim()`, `substring()`, `replace()`, `split()`, `contains()`, `startsWith()`, `length()` |
| `ExtractFunctionExecutor` | `extract` | `selector(html, css)`, `xpath(html, path)`, `regx(text, pattern)`, `jsonpath(json, path)` |
| `JsonFunctionExecutor` | `json` | `parse(text)`, `get(json, path)`, `toJson(obj)` |
| `DateFunctionExecutor` | `date` | `now()`, `format(date, pattern)`, `parse(text, pattern)`, `timestamp()` |
| `Base64FunctionExecutor` | `base64` | `encode(text)`, `decode(text)` |
| `MD5FunctionExecutor` | `md5` | `md5(text)` |
| `UrlFunctionExecutor` | `url` | `encode(url)`, `decode(url)`, `params(url)` |
| `FileFunctionExecutor` | `file` | `read(path)`, `write(path, content)`, `exists(path)` |
| `ListFunctionExecutor` | `list` | `new()`, `add(list, item)`, `get(list, index)`, `size(list)` |
| `RandomFunctionExecutor` | `random` | `number(min, max)`, `string(length)`, `uuid()` |
| `ThreadFunctionExecutor` | `thread` | `sleep(millis)`, `currentThread()` |

## FunctionExtension 扩展方法速查

| 类 | 扩展类型 | 核心方法示例 |
|---|---|---|
| `StringFunctionExtension` | `String` | `selector(css)`, `xpath(path)`, `regx(pattern)`, `jsonpath(path)`, `md5()`, `base64()`, `length()`, `matches(regex)` |
| `ResponseFunctionExtension` | `SpiderResponse` | `selector(css)`, `xpath(path)`, `regx(pattern)`, `jsonpath(path)` |
| `ElementFunctionExtension` | `Element` | `text()`, `html()`, `attr(name)`, `selector(css)`, `xpath(path)`, `parent()`, `children()` |
| `ElementsFunctionExtension` | `Elements` | `text()`, `html()`, `attr(name)`, `selector(css)`, `get(index)`, `size()` |
| `ListFunctionExtension` | `List` | `get(index)`, `size()`, `join(sep)`, `sort()`, `distinct()`, `first()`, `last()` |
| `ArrayFunctionExtension` | `Object[]` | `get(index)`, `size()`, `toList()` |
| `MapFunctionExtension` | `Map` | `get(key)`, `keys()`, `values()`, `containsKey(key)` |
| `DateFunctionExtension` | `Date` | `format(pattern)`, `timestamp()`, `after(date)`, `before(date)` |
| `ObjectFunctionExtension` | `Object` | `toString()`, `isNull()`, `isNotNull()` |
| `SqlRowSetExtension` | `SqlRowSet` | `get(columnName)`, `next()`, `toList()` |
