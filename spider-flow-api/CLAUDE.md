# CLAUDE.md — spider-flow-api

## Module Identity

`spider-flow-api` 是项目的**接口契约层**，被 `spider-flow-core` 和 `spider-flow-web` 依赖。

> ⚠️ **核心约束：本模块 pom.xml 不单独声明依赖**，所有依赖均继承自父 POM。模块内包含接口定义、公共模型和抽象基类（`CURDController` 使用了 Spring/MyBatis 注解，运行时通过父 POM 提供）。

---

## Rules for This Module

### DO ✅
- 保持接口纯粹：本模块 pom.xml 不单独声明依赖，所有依赖均来自父 POM
- 用 `default` 方法为接口提供合理的默认行为
- `SpiderContext` 的类型转换使用泛型方法 `<T> T get(key)`
- `CURDController` 是抽象基类，子类继承即可获得 CRUD 能力

### DON'T ❌
- **不要**在本模块 pom.xml 中添加新的依赖声明
- **不要**修改 `SpiderNode.jsonProperty` 的访问修饰符（外部通过 getter 访问）
- **不要**在 `SpiderContext` 中将 `running` 重置为 true

---

## Directory Map

```
spider-flow-api/src/main/java/org/spiderflow/
├── annotation/             # 自定义注解（运行时反射，生成前端语法提示）
│   ├── Comment.java        #   @Comment("说明")     标注方法/类用途
│   ├── Example.java        #   @Example("示例")     标注调用示例
│   └── Return.java         #   @Return({Class})     标注返回值类型（Class<?>[]，不是 String）
├── common/
│   └── CURDController.java # 通用 CRUD Controller 基类
├── concurrent/             # 线程池与任务提交策略
│   ├── SpiderFlowThreadPoolExecutor.java   # 全局线程池，支持创建 SubThreadPoolExecutor
│   ├── SpiderFutureTask.java               # 自定义 FutureTask
│   ├── ThreadSubmitStrategy.java           # 任务提交策略接口
│   ├── RandomThreadSubmitStrategy.java     # 随机策略（默认）
│   ├── LinkedThreadSubmitStrategy.java     # 链式顺序策略
│   ├── ChildPriorThreadSubmitStrategy.java # 子节点优先策略
│   └── ParentPriorThreadSubmitStrategy.java# 父节点优先策略
├── context/                # 执行上下文
│   ├── SpiderContext.java  #   继承 HashMap，持有 threadPool / futureQueue / running / rootNode
│   ├── SpiderContextHolder.java  # ThreadLocal 持有器
│   └── CookieContext.java  #   HTTP Cookie 管理
├── enums/
│   ├── FlowNoticeType.java # 通知类型（start / end / exception）
│   └── FlowNoticeWay.java  # 通知方式
├── executor/               # ★ 核心扩展接口（项目最重要的扩展点）
│   ├── ShapeExecutor.java  #   节点形状执行器
│   ├── FunctionExecutor.java # 表达式函数执行器
│   ├── FunctionExtension.java # 类型扩展方法
│   └── PluginConfig.java   #   插件配置
├── expression/
│   └── DynamicMethod.java  # 动态方法定义
├── io/
│   ├── SpiderResponse.java # HTTP 响应封装接口
│   ├── Line.java           # 日志行（行号 + 内容）
│   └── RandomAccessFileReader.java # 随机文件读取器
├── listener/
│   └── SpiderListener.java # 爬虫生命周期监听
├── model/                  # 公共数据模型
│   ├── SpiderNode.java     #   爬虫节点（核心，见下方详解）
│   ├── SpiderOutput.java   #   输出数据
│   ├── SpiderLog.java      #   日志模型
│   ├── JsonBean.java       #   统一响应 {code, message, data}
│   ├── Shape.java          #   节点形状描述（前端工具栏）
│   ├── Grammer.java        #   语法提示项（前端代码补全）
│   └── Plugin.java         #   插件描述
├── utils/
│   └── Maps.java           # Map 工具类
├── ExpressionEngine.java   # 表达式引擎接口
└── Grammerable.java        # 语法提示提供者接口
```

---

## Extension Interfaces（扩展接口详解）

### ShapeExecutor — 节点形状执行器

```java
public interface ShapeExecutor {
    // 接口常量（节点 JSON 属性中的 key）
    String LOOP_VARIABLE_NAME = "loopVariableName";
    String LOOP_COUNT = "loopCount";
    String THREAD_COUNT = "threadCount";

    // ★ 返回节点 shape 标识，必须与前端 XML 中 shape 字段完全一致
    String supportShape();

    // 节点执行逻辑（在线程池中运行）
    void execute(SpiderNode node, SpiderContext context, Map<String, Object> variables);

    // 返回 Shape 描述对象，null 表示不显示在工具栏
    default Shape shape() { return null; }

    // 执行完毕后是否允许继续执行下级节点（默认 true）
    default boolean allowExecuteNext(SpiderNode node, SpiderContext context, Map<String, Object> variables) { return true; }

    // 是否在线程池中异步运行（默认 true）；
    // 返回 false 时节点在当前线程同步执行，适用于无阻塞操作的轻量节点
    default boolean isThread() { return true; }
}
```

### FunctionExecutor — 表达式函数执行器

```java
public interface FunctionExecutor {
    // 函数前缀，如 "string"、"json"
    // 调用方式：前缀.方法名(参数)，如 string.lowercase('ABC')
    String getFunctionPrefix();
}
```

> **规则**：实现类中所有 public static 方法自动注册为函数，**必须**加 `@Comment` 注解。

### FunctionExtension — 类型扩展方法

```java
public interface FunctionExtension {
    // 返回要扩展的 Java 类型
    Class<?> support();
}
```

> 实现类中的方法第一个参数为被扩展类型的实例，调用时省略第一个参数：
> `StringFunctionExtension.regx(source, pattern)` → `${strVar.regx('<title>(.*?)</title>')}`

### SpiderListener — 生命周期监听

```java
public interface SpiderListener {
    void beforeStart(SpiderContext context);  // 任务启动前
    void afterEnd(SpiderContext context);     // 任务结束后
}
```

---

## SpiderNode — 核心模型

爬虫流程中的单个节点，包含属性、关系、条件和计数器。

| 方法 | 说明 | 注意事项 |
|------|------|----------|
| `getStringJsonValue(key)` | 读取节点 JSON 属性 | 自动 HTML 反转义，**不要**直接操作 jsonProperty |
| `getStringJsonValue(key, default)` | 读取属性，不存在时返回默认值 | |
| `getListJsonValue(keys...)` | 批量读取数组属性，多字段对齐 | 数组长度不一致时抛 ArrayIndexOutOfBoundsException |
| `addNextNode(node)` | 添加下级节点，自动建立双向关联 | |
| `getCondition(fromNodeId)` | 获取来自某节点的箭头条件表达式 | |
| `getExceptionFlow(fromNodeId)` | 异常流转：`"1"`=有异常走 / `"2"`=无异常走 | |
| `isTransmitVariable(fromNodeId)` | 是否传递变量（默认 true） | |
| `increment()` / `decrement()` | 原子计数器，供 ForkJoin 节点等待使用 | |
| `isDone()` | 递归检查本节点及所有祖先节点是否执行完毕 | |
| `hasLeftNode(nodeId)` | 判断某节点是否在祖先链路中 | 首次调用会缓存 parentNodes |

---

## SpiderContext — 执行上下文

继承 `HashMap<String, Object>`，贯穿整个爬虫任务生命周期。

| 字段/方法 | 类型 | 说明 |
|-----------|------|------|
| `threadPool` | `SubThreadPoolExecutor` | 本流程的子线程池 |
| `futureQueue` | `LinkedBlockingQueue<Future<?>>` | 任务 Future 队列，引擎循环消费 |
| `running` | `volatile boolean` | 运行标志，**只能从 true → false**（用于中止任务） |
| `rootNode` | `SpiderNode` | 流程根节点 |
| `cookieContext` | `CookieContext` | HTTP Cookie 共享上下文 |
| `flowId` | `String` | 流程 ID（测试模式下为 null） |
| `id` | `String` | 本次执行的唯一 ID（UUID，去掉“-”） |
| `get(key)` | `<T> T` | 泛型读取，自动转型 |
| `get(key, defaultValue)` | `<T> T` | 读取，不存在时返回默认值 |
| `getOutputs()` | `List<SpiderOutput>` | 获取输出列表（基类返回空列表，子类覆写） |
| `addOutput(output)` | | 添加输出数据（基类空实现，子类覆写） |
| `pause(nodeId, event, key, value)` | | 调试暂停（基类空实现，WebSocketContext 覆写） |
| `resume()` | | 恢复暂停的调试流程 |
| `stop()` | | 停止调试流程 |

> **线程安全**：`SpiderContext` 继承非线程安全的 `HashMap`，但核心并发字段本身是线程安全的：`running`（volatile boolean）、`futureQueue`（`LinkedBlockingQueue`）、`threadPool`（`SubThreadPoolExecutor`）。直接 `put/get` 操作在多线程下仍需注意竞态条件。

---

## Annotation Convention

`FunctionExecutor` / `FunctionExtension` 的所有 public 方法必须按以下格式添加注解：

```java
@Comment("函数用途说明")           // 必填，前端代码提示展示
@Example("string.lowercase('ABC')") // 可选，前端示例展示
@Return({String.class})            // 可选，参数类型是 Class<?>[]（不是 String）
public static String lowercase(String str) { ... }
```

这些注解在运行时通过反射读取，生成 `/spider/grammers` 接口的语法提示数据。

---

## Grammerable — 语法提示接口

```java
public interface Grammerable {
    List<Grammer> grammers();  // 返回变量的语法提示列表（⚠️ 方法名是 grammers()，不是 getGrammers()）
}
```

> 实现该接口的 `ShapeExecutor`（如 `RequestExecutor`、`ExecuteSQLExecutor`）会向前端暴露节点输出变量的属性提示。前端编辑器中输入变量名 `.` 时触发代码补全，数据来源为 `/spider/grammers` 接口。

---

## ThreadSubmitStrategy — 线程提交策略

`SubThreadPoolExecutor` 创建时通过 `ThreadSubmitStrategy` 接口选择任务提交策略，影响节点执行顺序：

| 策略类 | 行为 |
|---|---|
| `RandomThreadSubmitStrategy` | 随机选择就绪任务提交（**默认**） |
| `LinkedThreadSubmitStrategy` | 按链式顺序提交 |
| `ChildPriorThreadSubmitStrategy` | 子节点优先提交 |
| `ParentPriorThreadSubmitStrategy` | 父节点优先提交 |

> 策略通过 `SubThreadPoolExecutor` 构造函数注入，运行时由引擎根据流程结构自动选择。
