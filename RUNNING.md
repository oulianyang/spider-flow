# spider-flow 项目运行指南（零基础版）

本项目是一个基于 **Java 8 + Spring Boot** 的可视化爬虫平台，使用 **MySQL** 作为数据库。

---

## 环境要求

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| JDK | 1.8 | Java 运行环境 |
| Maven | 3.x | 项目构建工具 |
| MySQL | 5.7+ | 数据库 |

---

## 第一步：安装 JDK 8

1. 访问 [Adoptium](https://adoptium.net/temurin/releases/?version=8) 下载 JDK 8
2. 选择 **Windows x64 JDK (.msi)** 安装包
3. 安装时 **务必勾选"设置 JAVA_HOME"** 选项
4. 安装完成后打开 PowerShell 验证：

```powershell
java -version
```

看到 `openjdk version "1.8.x"` 即安装成功。

---

## 第二步：安装 Maven

1. 访问 [Maven 官网](https://maven.apache.org/download.cgi) 下载 `apache-maven-x.x.x-bin.zip`
2. 解压到目录，例如 `C:\maven`
3. 配置环境变量：
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 新建系统变量：`MAVEN_HOME` = `C:\maven`
   - 编辑 `Path` 变量，追加：`C:\maven\bin`
4. 重新打开 PowerShell 验证：

```powershell
mvn -version
```

显示版本号即安装成功。

> **加速提示**：可配置阿里云 Maven 镜像，编辑 `C:\maven\conf\settings.xml`，在 `<mirrors>` 节点内添加：
> ```xml
> <mirror>
>   <id>aliyunmaven</id>
>   <mirrorOf>*</mirrorOf>
>   <name>阿里云公共仓库</name>
>   <url>https://maven.aliyun.com/repository/public</url>
> </mirror>
> ```

---

## 第三步：安装 MySQL

1. 访问 [MySQL 官网](https://dev.mysql.com/downloads/installer/) 下载 MySQL Installer for Windows
2. 安装过程中，设置 root 密码（请记住该密码，后续需配置到项目中）
3. 安装完成后，打开 MySQL 命令行或 MySQL Workbench
4. 执行项目自带的数据库初始化脚本：

```sql
source <项目根目录>/db/spiderflow.sql
```

> 例如 Windows 上：`source f:/yl/workspace/github/spider-flow/db/spiderflow.sql`
> Linux/Mac 上：`source /home/user/spider-flow/db/spiderflow.sql`

---

## 第四步：修改数据库配置

修改配置文件中的数据库连接信息：

**文件路径**：`spider-flow-web/src/main/resources/application.properties`

```properties
spring.datasource.username=root
spring.datasource.password=<你的MySQL密码>
spring.datasource.url=jdbc:mysql://localhost:3306/spiderflow?useUnicode=true&characterEncoding=utf-8&useSSL=false
```

其他可配置项：

```properties
# 服务端口（默认 8088）
server.port=8088

# 爬虫任务工作空间
spider.workspace=/data/spider

# 定时任务开关（设为 true 才生效）
spider.job.enable=false
```

> ⚠️ **定时任务配置**：如果需要使用 Cron 定时执行爬虫，必须将 `spider.job.enable` 设为 `true`，否则配置的 Cron 表达式不会生效。

---

## 第五步：编译打包项目

打开 PowerShell，进入项目根目录：

```powershell
cd f:\yl\workspace\github\spider-flow
```

执行 Maven 打包命令（首次执行需下载依赖，耗时较长）：

```powershell
mvn clean package -DskipTests
```

出现 `BUILD SUCCESS` 表示编译成功，生成文件位于：

```
spider-flow-web/target/spider-flow.jar
```

---

## 第六步：启动项目

```powershell
java -jar spider-flow-web/target/spider-flow.jar
```

看到以下日志表示启动成功：

```
Started SpiderApplication in xx seconds
```

---

## 第七步：访问系统

打开浏览器，访问：

```
http://localhost:8088
```

即可进入 spider-flow 可视化爬虫界面。

---

## Docker 方式运行（可选）

需提前安装 Docker Desktop，并确保本机 MySQL 可被容器访问。

```powershell
# 1. 编译项目
mvn clean package -DskipTests

# 2. 构建 Docker 镜像
docker build -t spider-flow .

# 3. 启动容器
docker run -d -p 8088:8088 --name spider-flow spider-flow
```

> 注意：Docker 方式运行时，容器内访问 `localhost` 指向的是容器自身，需将 `application.properties` 中的数据库地址改为宿主机 IP 或 `host.docker.internal`。

---

## 常见问题排查

### `java 不是内部或外部命令`
- 原因：JDK 未安装或环境变量未配置
- 解决：重新安装 JDK，确保勾选"设置 JAVA_HOME"

### `mvn 不是内部或外部命令`
- 原因：Maven 环境变量配置有误
- 解决：检查 Path 中是否包含 `C:\maven\bin`

### `Access denied for user 'root'@'localhost'`
- 原因：MySQL 密码与配置不符
- 解决：修改 `application.properties` 中的 `spring.datasource.password`

### `Unknown database 'spiderflow'`
- 原因：未执行数据库初始化脚本
- 解决：在 MySQL 中执行 `db/spiderflow.sql`

### Maven 编译失败 / 下载超时
- 原因：网络问题导致依赖下载失败
- 解决：配置阿里云 Maven 镜像（见第二步加速提示）

### 端口 8088 被占用
- 原因：其他程序占用了该端口
- 解决：修改 `application.properties` 中的 `server.port` 为其他端口

---

## SpiderFlow 爬虫使用指南

### 一、创建爬虫

SpiderFlow 采用**可视化流程图**方式定义爬虫，通过 Web UI 拖拽节点并连线来构建。

**步骤：**
1. 启动应用后访问 `http://localhost:8088`
2. 点击"新建"创建一个爬虫流程
3. 在画布上拖入节点，连线构成执行流程
4. 点击"保存"存储流程图

**可用节点类型：**

| 节点 | shape 值 | 说明 |
|------|---------|------|
| 开始节点 | `start` | 流程入口，必须存在 |
| 请求节点 | `request` | 发起 HTTP 请求 |
| 变量节点 | `variable` | 定义/修改变量 |
| 函数节点 | `function` | 执行自定义表达式 |
| 循环节点 | `loop` | 循环执行后续节点 |
| 输出节点 | `output` | 输出抓取结果 |
| SQL节点 | `executeSql` | 执行数据库操作 |
| 子流程节点 | `process` | 调用另一个爬虫流程 |
| 等待节点 | `forkJoin` | 等待所有并行分支执行完毕 |
| 注释节点 | `comment` | 无实际功能，用于说明 |

---

### 二、传递参数

#### 1. 通过 API 传参（外部调用）

调用 `/rest/run/{id}` 接口时，通过 RequestBody 传入参数，这些参数会成为流程的初始变量：

```bash
# 同步调用，传入参数
curl -X POST -H "Content-Type: application/json" \
  -d '{"keyword": "手机", "page": 1}' \
  http://localhost:8088/rest/run/{爬虫ID}
```

在流程中通过 `${keyword}`、`${page}` 引用这些参数。

#### 2. 变量节点（variable）

在流程中使用变量节点定义中间变量：
- **变量名**：`startUrl`
- **变量值**（支持表达式）：`https://example.com/search?q=${keyword}`

#### 3. 节点间变量传递

变量自动沿箭头方向传递给下一个节点。连线上可设置**条件表达式**，决定是否继续执行：
- 条件示例：`${resp.statusCode == 200}`（只有请求成功才走这条路径）
- 异常流转：箭头可配置"出现异常流转"或"未出现异常流转"

#### 4. 循环参数

循环节点支持：
- **循环次数/集合**：填入表达式，如 `10`（循环10次）或 `${extract.xpaths(resp.html,'//a/@href')}`（遍历链接列表）
- **循环下标变量名**：如 `i`，存入当前下标
- **循环 item 变量名**：默认 `item`，存入当前集合元素
- **起始/结束位置**：`loopStart`、`loopEnd`

---

### 三、HTTP 请求（Request 节点）

**请求配置项：**

| 属性 | 说明 | 示例 |
|------|------|------|
| `url` | 请求地址（支持表达式） | `https://api.example.com/data?page=${page}` |
| `method` | 请求方法 | GET / POST |
| `timeout` | 超时时间（ms） | `60000` |
| `sleep` | 延迟执行（ms，支持表达式） | `2000` |
| `retryCount` | 重试次数 | `3` |
| `retryInterval` | 重试间隔（ms） | `1000` |
| `proxy` | 代理（支持表达式） | `127.0.0.1:8080` |
| `follow-redirect` | 是否跟随重定向 | `1`=是，`0`=否 |
| `response-charset` | 强制响应编码 | `UTF-8` |
| `repeat-enable` | URL 去重（布隆过滤器） | `1`=启用 |

**请求参数（Query String）：**
- 参数名：`keyword`  参数值：`${keyword}`

**请求 Body 类型：**
- `form-data`：表单提交，支持文件上传（type=file）
- `raw`：原始 Body，可指定 Content-Type，内容支持表达式

**请求 Header：**
- Header 名：`User-Agent`  Header 值：`Mozilla/5.0...`

**Cookie 管理：**
- 全局 Cookie（设置在 Start 节点，所有请求共享）
- 节点 Cookie（仅当前请求使用）
- 自动 Cookie（`cookie-auto-set=1`，自动保存响应 Set-Cookie）

---

### 四、获取数据

请求完成后，响应对象自动存入变量 **`resp`**。

#### resp 对象属性

| 表达式 | 说明 |
|--------|------|
| `${resp.statusCode}` | HTTP 状态码 |
| `${resp.html}` | 响应 HTML/文本内容 |
| `${resp.json}` | 解析为 JSON 对象 |
| `${resp.title}` | 页面标题 |
| `${resp.url}` | 当前 URL（重定向后） |
| `${resp.cookies}` | 响应 Cookie Map |
| `${resp.headers}` | 响应 Header Map |
| `${resp.bytes}` | 响应字节数组 |
| `${resp.contentType}` | Content-Type |

#### 数据提取函数

**XPath 提取：**
```
${extract.xpath(resp.html, '//title/text()')}          # 提取单个
${extract.xpaths(resp.html, '//a/@href')}               # 提取列表
${extract.xpath(resp.element(), '//div[@class="item"]')} # 使用 Element 对象
```

**CSS 选择器提取：**
```
${extract.selector(resp.html, 'div.title', 'text')}           # 文本
${extract.selector(resp.html, 'a.link', 'attr', 'href')}      # 属性
${extract.selectors(resp.html, 'li.item', 'element')}         # 元素列表
${extract.selectors(resp.html, 'div.content')}                # HTML列表
```

**正则表达式提取：**
```
${extract.regx(resp.html, '<title>(.*?)</title>')}           # 提取第一个匹配
${extract.regx(resp.html, '"id":"(\d+)"', 1)}                # 指定分组
${extract.regxs(resp.html, '<h2>(.*?)</h2>')}                # 提取所有匹配
${extract.regxs(resp.html, '<a.*?>(.*?)</a>', 1)}            # 指定分组所有匹配
```

**JSONPath 提取（针对 JSON 响应）：**
```
${extract.jsonpath(resp.json, '$.code')}
${extract.jsonpath(resp.json, '$.data.list[*].name')}
```

#### 其他常用函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `json.parse(str)` | 字符串转 JSON | `${json.parse(resp.html)}` |
| `json.stringify(obj)` | 对象转 JSON 字符串 | `${json.stringify(data)}` |
| `string.substring(s,0,5)` | 截取字符串 | `${string.substring(resp.html,0,100)}` |
| `string.replace(s,a,b)` | 替换 | `${string.replace(s,' ','')}` |
| `string.split(s,regx)` | 分割 | `${string.split(s,',')}` |
| `list.length(l)` | 列表长度 | `${list.length(links)}` |
| `list.split(l,10)` | 列表分片 | `${list.split(links,10)}` |
| `base64.encode/decode` | Base64 编解码 | `${base64.encode(str)}` |
| `md5(str)` | MD5 哈希 | `${md5(str)}` |

---

### 五、输出数据（Output 节点）

输出节点定义最终抓取结果：

**输出字段配置：**
- 输出名：`title`  输出值：`${extract.xpath(resp.html,'//h1/text()')}`
- 输出名：`price`  输出值：`${extract.regx(resp.html,'"price":"(.*?)"',1)}`

**输出目标：**
- `output-all=1`：输出所有变量（调试用）
- `output-database=1`：写入数据库（需配置数据源ID和表名）
- `output-csv=1`：写入 CSV 文件（指定文件路径和编码）

---

### 六、数据库操作（ExecuteSQL 节点）

SQL 中使用 `#变量名#` 作为参数占位符（自动转为预编译参数）：

```sql
-- 查询（结果存入变量 rs）
SELECT * FROM products WHERE name LIKE #keyword#

-- 插入
INSERT INTO products (title, price) VALUES (#title#, #price#)

-- 批量插入（参数为List时自动批量执行）
INSERT INTO items (name) VALUES (#nameList#)
```

**Statement 类型：**
- `select`：查询列表 → `rs` 为 `List<Map>`
- `selectOne`：查询单条 → `rs` 为 `Map`
- `selectInt`：查询数字 → `rs` 为 `Integer`
- `insert` / `update` / `delete`：增删改 → `rs` 为影响行数
- `insertofPk`：插入并返回主键 → `rs` 为主键值

---

### 七、API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/spider/list?page=1&limit=10` | GET | 分页获取爬虫列表 |
| `/spider/save` | POST | 保存爬虫 |
| `/spider/get?id=xxx` | GET | 获取爬虫详情 |
| `/spider/remove?id=xxx` | GET | 删除爬虫 |
| `/spider/start?id=xxx` | GET | 启动定时任务 |
| `/spider/stop?id=xxx` | GET | 停止定时任务 |
| `/spider/run?id=xxx` | GET | 手动触发一次 |
| `/spider/cron?id=xxx&cron=...` | GET | 设置 Cron 表达式 |
| `/rest/run/{id}` | POST | **同步运行**（支持传参，返回结果） |
| `/rest/runAsync/{id}` | GET | **异步运行**（返回 taskId） |
| `/rest/status/{taskId}` | GET | 查询异步任务状态 |
| `/rest/stop/{taskId}` | GET | 停止异步任务 |

---

### 八、完整示例流程

**场景：抓取某网站商品列表并存入数据库**

```
[开始]
  ↓ （定义变量：keyword="手机", page=1）
[变量节点]
  ↓
[请求节点] url=https://api.example.com/search?keyword=${keyword}&page=${page}
  ↓ （resp 存入变量）
[函数节点] links = extract.xpaths(resp.html, '//a[@class="item"]/@href')
  ↓
[循环节点] 循环次数=${list.length(links)}，item=当前链接
  ↓
[请求节点] url=https://example.com${item}
  ↓
[输出节点]
  title = ${extract.xpath(resp.html, '//h1/text()')}
  price = ${extract.regx(resp.html, '"price":"(.*?)"', 1)}
  → 输出到数据库 / CSV
```

---

### 九、注意事项

1. **表达式语法**：所有需要动态计算的地方都用 `${...}` 包裹，如 `${resp.html}`、`${page + 1}`
2. **异常处理**：节点执行异常时，异常对象存入变量 `ex`，可通过箭头条件 `${ex == null}` 控制流程
3. **线程数配置**：Start 节点可配置单任务线程数（`threadCount`），默认8个
4. **定时任务**：通过 `/spider/cron` 设置 Cron 表达式，`/spider/start` 启动
5. **子流程**：Process 节点可调用另一爬虫流程，变量自动传递

---

## 十一、外部项目通过 iframe 嵌入爬虫并传参

### 背景

当其他项目（如内部业务系统）需要调用 spider-flow 的可视化爬虫时，可通过 iframe 嵌入编辑器页面，并通过 URL 查询参数传递任意业务数据，这些参数会自动成为爬虫流程的**初始变量**，在流程中直接用 `${变量名}` 引用。

---

### 接入方式

**外部项目嵌入 iframe：**

```html
<iframe 
  src="http://spider-flow-host:8088/editor.html?id=爬虫ID&keyword=手机&page=1&category=电子"
  width="100%" height="600px">
</iframe>
```

**URL 参数说明：**

| 参数 | 是否必填 | 说明 |
|------|---------|------|
| `id` | 是 | 爬虫流程 ID（系统内置参数，不会传入流程变量） |
| 其他任意参数 | 否 | 自动成为爬虫流程的初始变量，参数名即变量名 |

---

### 爬虫配置中使用参数

在流程中直接用 `${变量名}` 引用 URL 参数：

```
[开始]
  ↓
[请求节点]
  URL: https://api.example.com/search?keyword=${keyword}&page=${page}&category=${category}
  ↓
[输出节点]
  title = ${extract.xpath(resp.html, '//h1/text()')}
```

上例中 `keyword`、`page`、`category` 均从 iframe URL 参数中自动获取。

---

### 参数传递流程图

```
外部项目页面
    │
    └─► iframe src="editor.html?id=xxx&keyword=手机&page=2"
              │
              ├─► editor.js getUrlParameters() 读取 URL 参数
              │    返回：{ keyword: '手机', page: '2' }
              │
              └─► 点击"测试"时通过 WebSocket 发送：
                   { eventType: 'test', message: xml, parameters: {...} }
                        │
                        ├─► WebSocketEditorServer.java 读取 parameters
                        │
                        └─► Spider.runWithTest(root, context, variables)
                             变量 keyword=手机、page=2 自动注入流程
```

---

### 注意事项

1. **参数名不要使用 `id`**，这是系统内置参数，会被自动过滤不传入流程变量
2. **参数值支持中文**，前端会自动进行 URL 解码（`decodeURIComponent`）
3. **测试和调试均支持**，无论是点击"测试"还是"调试"按钮，URL 参数均会传入
4. **REST API 调用**（`/rest/run/{id}`）是另一种更灵活的传参方式，适合后端对后端调用，无需改造前端

---

### 两种方式对比

| 对比项 | iframe 嵌入（前端） | REST API（后端） |
|--------|-------------------|----------------|
| 调用方式 | `<iframe src="...">` | `POST /rest/run/{id}` |
| 参数格式 | URL 查询参数 `?key=value` | JSON Body `{"key":"value"}` |
| 适用场景 | 可视化配置 + 测试 | 生产环境程序化调用 |
| 参数注入机制 | 前端读取 → WebSocket 传递 → 初始变量 | 直接作为初始变量传入 |
| 结果获取 | 页面实时展示 | HTTP 响应体直接返回 |

---

## 十二、处理登录

SpiderFlow 完整支持各类登录场景，核心机制是：**请求节点发送登录请求 → 响应 Cookie/Token 自动保存 → 后续请求自动携带**。

### 方式一：Cookie 自动管理（最常用，适合 Session 登录）

适合传统 Web 登录（服务端下发 Set-Cookie）。

**流程设计：**

```
[开始]
  ↓
[请求节点 - 登录] POST https://example.com/login
  参数: username=xxx, password=xxx
  cookie-auto-set = 1  ← 登录响应的 Cookie 自动存入上下文
  ↓
[请求节点 - 抓取] GET https://example.com/data
  cookie-auto-set = 1  ← 自动携带上次登录的 Cookie，无需手动配置
  ↓
[输出节点]
```

**原理**：`cookie-auto-set=1`（默认开启）时，登录请求的响应 Cookie 会自动存入 `CookieContext`，后续同一流程内所有请求节点都会自动携带这些 Cookie，无需任何额外配置。

---

### 方式二：Token / JWT 登录（适合前后端分离 API）

适合登录成功后返回 Token，后续请求在 Header 中携带 Token 的场景。

**流程设计：**

```
[开始]
  ↓
[请求节点 - 登录] POST https://api.example.com/login
  Body (raw): {"username":"xxx","password":"xxx"}
  Content-Type: application/json
  ↓ （resp.json 中有 {"code":0,"token":"abc123..."} ）
[变量节点]
  token = ${extract.jsonpath(resp.json, '$.token')}
  ↓
[请求节点 - 抓取] GET https://api.example.com/data
  Header: Authorization = Bearer ${token}
  ↓
[输出节点]
```

**关键步骤说明：**

| 步骤 | 配置 |
|------|------|
| 登录请求 | Body 类型选 `raw`，Content-Type 填 `application/json`，内容填 `${"username":"xxx","password":"xxx"}` |
| 提取 Token | 变量节点中使用 `${extract.jsonpath(resp.json, '$.token')}` 将 Token 存入变量 `token` |
| 后续请求 | Header 配置：名=`Authorization`，值=`Bearer ${token}` |

---

### 方式三：手动设置 Cookie（适合已有 Cookie 字符串）

适合从浏览器开发者工具复制 Cookie 后直接使用。

**流程设计：**

```
[开始]
  ↓
[请求节点 - 抓取] GET https://example.com/data
  Cookie: SESSION = abc123...（直接填写从浏览器复制的值）
  ↓
[输出节点]
```

在请求节点的 **Cookie 配置区**，手动填写：
- Cookie 名：`SESSION`（或 `JSESSIONID`、`PHPSESSID` 等实际名称）
- Cookie 值：从浏览器复制的完整值，支持表达式如 `${myCookie}`

---

### 登录失败判断与重试

可通过箭头条件判断登录是否成功，失败时重新登录：

```
[请求节点 - 登录]
  ↓ 条件：${resp.statusCode == 200 && extract.jsonpath(resp.json,'$.code') == 0}
[请求节点 - 抓取数据]
  ↓
[输出节点]

[请求节点 - 登录] → 条件不满足时（登录失败）
  ↓ 箭头条件：${resp.statusCode != 200}
[函数节点] 记录日志 / 抛出异常
```

---

### 完整登录爬虫示例（JSON API + Token）

**场景：登录 API 获取 Token，然后抓取需要鉴权的数据列表**

```
[开始]
  变量: username=admin, password=123456
  ↓
[请求节点] 登录
  URL:    https://api.example.com/auth/login
  Method: POST
  Body:   raw / application-json
  Body内容: {"username":"${username}","password":"${password}"}
  ↓
[变量节点] 提取 Token
  accessToken = ${extract.jsonpath(resp.json, '$.data.access_token')}
  userId      = ${extract.jsonpath(resp.json, '$.data.user_id')}
  ↓
[请求节点] 获取数据列表
  URL:    https://api.example.com/api/items?page=1
  Method: GET
  Header: Authorization = Bearer ${accessToken}
  Header: X-User-Id     = ${userId}
  ↓
[循环节点] 遍历数据
  循环集合: ${extract.jsonpath(resp.json, '$.data.list')}
  item变量名: item
  ↓
[输出节点]
  id    = ${item.id}
  name  = ${item.name}
  price = ${item.price}
  → 输出到数据库 / CSV
```

---

### 登录方式对比

| 登录方式 | 适用场景 | 后续请求鉴权方式 |
|---------|---------|----------------|
| Cookie 自动管理 | 传统 Web、Session 登录 | 自动携带 Cookie（无需配置） |
| Token/JWT | RESTful API、前后端分离 | Header 携带 `Authorization: Bearer xxx` |
| 手动 Cookie | 调试、已有有效 Cookie | 手动填写 Cookie 名和值 |
