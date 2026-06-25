# spider-flow 内网环境部署指南

> 本指南适用于在无法访问外网的内网环境中部署 spider-flow 爬虫平台。

---

## 目录

- [1. 环境要求](#1-环境要求)
- [2. 离线准备（在外网机器完成）](#2-离线准备在外网机器完成)
- [3. 部署步骤](#3-部署步骤)
- [4. 配置说明](#4-配置说明)
- [5. 启动与验证](#5-启动与验证)
- [6. 常见问题](#6-常见问题)
- [附录](#附录)

---

## 1. 环境要求

### 1.1 服务器配置

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Linux / Windows Server | CentOS 7+ / Windows Server 2016+ |
| CPU | 2 核 | 4 核+ |
| 内存 | 4 GB | 8 GB+ |
| 磁盘 | 20 GB | 50 GB+（日志和历史版本需要空间） |

### 1.2 软件依赖

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| JDK | 1.8（Java 8） | 必须，推荐 Oracle JDK 或 OpenJDK 8 |
| MySQL | 5.7+ | 必须，存储流程和配置数据 |
| Maven | 3.x | 仅编译时需要，运行时不需要 |

### 1.3 网络端口

| 端口 | 协议 | 说明 |
|------|------|------|
| 8088 | TCP | Web 服务端口（必须） |
| 3306 | TCP | MySQL 端口（如果数据库在其他服务器） |
| 465 | TCP | SMTP SSL 端口（如果使用邮件通知功能） |

---

## 2. 离线准备（在外网机器完成）

> ⚠️ 以下步骤需要在**能访问外网的机器**上完成，然后将产物拷贝到内网服务器。

### 2.1 准备 JDK 8 安装包

**下载地址：**
- Oracle JDK: https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html
- OpenJDK: https://adoptium.net/temurin/releases/?version=8

**下载文件示例：**
- Linux: `OpenJDK8U-jdk_x64_linux_hotspot_8uXXXbXX.tar.gz`
- Windows: `OpenJDK8U-jdk_x64_windows_hotspot_8uXXXbXX.msi`

### 2.2 准备 MySQL 安装包

**下载地址：**
- https://dev.mysql.com/downloads/mysql/5.7.html#downloads
- 或使用公司内部 MySQL 安装源

**下载文件：**
- Linux: `mysql-5.7.xx-linux-glibc2.12-x86_64.tar.gz`（二进制包）
- Windows: `mysql-installer-community-5.7.xx.msi`

### 2.3 准备 Maven（编译时需要）

**下载地址：**
- https://maven.apache.org/download.cgi

**下载文件：**
- `apache-maven-3.8.x-bin.tar.gz`

### 2.4 编译打包项目

在外网机器上执行：

```bash
# 1. 克隆项目
git clone https://github.com/ssssssss-team/spider-flow.git
cd spider-flow

# 2. 编译打包（跳过测试）
mvn clean package -DskipTests

# 3. 打包产物位置
# spider-flow-web/target/spider-flow.jar
```

### 2.5 配置 Maven 内网镜像（可选）

如果内网有私有 Maven 仓库，编辑 `~/.m2/settings.xml`：

```xml
<mirrors>
  <mirror>
    <id>internal-repo</id>
    <mirrorOf>*</mirrorOf>
    <name>Internal Repository</name>
    <url>http://内网仓库地址/repository/maven-public/</url>
  </mirror>
</mirrors>
```

如果没有内网仓库，使用 2.6 节的离线仓库方式。

### 2.6 准备 Maven 离线仓库（可选，用于内网二次编译）

```bash
# 复制本地 Maven 仓库
# Linux/Mac: ~/.m2/repository
# Windows: C:\Users\你的用户名\.m2\repository

# 打包整个仓库目录
tar -czf maven-repo.tar.gz -C ~ .m2/repository
```

### 2.7 准备 Selenium WebDriver（可选，使用 Selenium 插件时需要）

如果需要使用 Selenium 浏览器自动化插件，需要下载对应浏览器的 WebDriver：

| 浏览器 | 版本 | 下载地址 |
|--------|------|----------|
| Chrome | ≤ 114 | https://registry.npmmirror.com/-/binary/chromedriver/ |
| Chrome | ≥ 115 | https://googlechromelabs.github.io/chrome-for-testing/ （国内镜像：https://registry.npmmirror.com/-/binary/chrome-for-testing/ ） |
| Firefox | 所有版本 | https://github.com/mozilla/geckodriver/releases |

> ⚠️ Chrome 115 起改用 Chrome for Testing (CfT) 发布，不再上传到旧的 chromedriver 仓库。
> 下载时选择与服务器 Chrome 版本**完全一致**的 ChromeDriver，版本号不匹配会导致启动失败。

### 2.8 整理部署包

将以下文件打包到一个文件夹：

```
deploy-package/
├── spider-flow.jar              # 编译好的 JAR 包
├── spiderflow.sql               # 数据库初始化脚本（来自源码 db/spiderflow.sql）
├── jdk-8uXXX-linux-x64.tar.gz   # JDK 安装包（如服务器未安装）
├── mysql-5.7.xx.tar.gz          # MySQL 安装包（如服务器未安装）
├── application.properties       # 配置文件（需修改）
├── chromedriver                 # Chrome WebDriver（可选）
├── geckodriver                  # Firefox WebDriver（可选）
└── maven-repo.tar.gz            # Maven 仓库（可选）
```

> 上传到服务器后，建议将整个 `deploy-package` 内容放置在 `/opt/spider-flow/` 目录下，后续步骤中的路径均基于此目录。

---

## 3. 部署步骤

### 3.1 上传文件到内网服务器

```bash
# 使用 scp、sftp 或 U 盘将 deploy-package 传输到内网服务器
# 示例路径：/opt/spider-flow/
```

### 3.2 安装 JDK 8

**Linux:**

```bash
# 解压
tar -xzf jdk-8uXXX-linux-x64.tar.gz -C /usr/local/

# 配置环境变量
cat >> /etc/profile << 'EOF'
export JAVA_HOME=/usr/local/jdk1.8.0_XXX
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib
EOF

# 使环境变量生效
source /etc/profile

# 验证
java -version
# 应输出：java version "1.8.0_XXX"
```

**Windows:**

```powershell
# 1. 运行 MSI 安装程序，按提示安装
# 2. 配置环境变量（注意：%JAVA_HOME% 是 CMD 语法，PowerShell 中应使用 $env:JAVA_HOME）
$javaHome = "C:\Program Files\Java\jdk1.8.0_XXX"
[Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "Machine")
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$javaHome\bin", "Machine")

# 3. 重新打开终端（环境变量在新终端中生效），验证
java -version
```

### 3.3 安装 MySQL

**Linux（二进制安装）：**

```bash
# 1. 解压
tar -xzf mysql-5.7.xx-linux-glibc2.12-x86_64.tar.gz -C /usr/local/
mv /usr/local/mysql-5.7.xx-linux-glibc2.12-x86_64 /usr/local/mysql

# 2. 创建用户和目录
groupadd mysql
useradd -r -g mysql mysql
mkdir -p /data/mysql
chown -R mysql:mysql /data/mysql

# 3. 初始化数据库
/usr/local/mysql/bin/mysqld --initialize --user=mysql --datadir=/data/mysql
# 记录生成的临时密码

# 4. 启动 MySQL
/usr/local/mysql/bin/mysqld_safe --user=mysql &

# 5. 登录并修改密码
/usr/local/mysql/bin/mysql -u root -p
# 输入临时密码

# 6. 在 MySQL 命令行中执行：
ALTER USER 'root'@'localhost' IDENTIFIED BY '你的新密码';
FLUSH PRIVILEGES;
```

**Windows:**

```powershell
# 1. 运行 MSI 安装程序
# 2. 按提示设置 root 密码
# 3. 确保 MySQL 服务已启动
Get-Service MySQL*
```

### 3.4 初始化数据库

> ⚠️ `spiderflow.sql` 脚本中已包含 `CREATE DATABASE` 和 `USE` 语句，会自动创建数据库。

> ⚠️ 以下命令假设 `spiderflow.sql` 已放置在 `/opt/spider-flow/` 目录下。原始文件位于源码仓库的 `db/spiderflow.sql`，部署时需拷贝到服务器的 `/opt/spider-flow/` 目录。

**方式一：直接导入（推荐，数据库不存在时）**

```bash
# 登录 MySQL 并导入
mysql -u root -p < /opt/spider-flow/spiderflow.sql
```

**方式二：如果数据库已存在**

```bash
# 1. 先登录 MySQL，注释掉 spiderflow.sql 前两行
#    # CREATE DATABASE spiderflow;
#    # USE spiderflow;

# 2. 然后指定数据库导入
mysql -u root -p spiderflow < /opt/spider-flow/spiderflow.sql
```

**方式三：手动创建后导入**

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库（如果 sql 脚本中已有此语句，可跳过）
CREATE DATABASE spiderflow DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 导入初始化脚本
mysql -u root -p spiderflow < /opt/spider-flow/spiderflow.sql
```

### 3.5 创建日志和工作目录

```bash
# Linux
mkdir -p /data/spider
chmod 755 /data/spider

# Windows（PowerShell）
New-Item -ItemType Directory -Path "C:\data\spider" -Force
```

---

## 4. 配置说明

### 4.1 修改配置文件

配置文件位置：`spider-flow.jar` 内的 `application.properties`

**方式一：外部配置文件（推荐）**

在 JAR 包同目录创建 `application.properties`，Spring Boot 会自动加载外部配置文件覆盖内置配置。

**方式二：JVM 参数传入**

```bash
java -jar spider-flow.jar \
  --spring.datasource.url="jdbc:mysql://192.168.1.100:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true" \
  --spring.datasource.username=root \
  --spring.datasource.password=your_password
```

### 4.2 完整配置文件示例

```properties
# === 服务配置 ===
server.port=8088
logging.level.root=INFO
spring.mvc.favicon.enabled=false

# === 数据源配置（必须修改）===
# 注意：com.mysql.jdbc.Driver 适用于 MySQL Connector/J 5.x（Spring Boot 2.0.7 默认）
# 如果升级到 MySQL Connector/J 8.x，需改为 com.mysql.cj.jdbc.Driver
spring.datasource.driver-class-name=com.mysql.jdbc.Driver
spring.datasource.username=root
spring.datasource.password=你的MySQL密码

# Linux 示例
# MySQL 5.x 使用：
# spring.datasource.url=jdbc:mysql://192.168.1.100:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true
# MySQL 8.0+ 需额外添加 allowPublicKeyRetrieval=true（使用 caching_sha2_password 认证时必需）：
spring.datasource.url=jdbc:mysql://192.168.1.100:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true

# Windows 示例（如果 MySQL 在本机）
# spring.datasource.url=jdbc:mysql://localhost:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true

# === 爬虫引擎配置 ===
spider.thread.max=64
spider.thread.default=8
spider.job.enable=true

# Linux
spider.workspace=/data/spider
# Windows
# spider.workspace=C:/data/spider

spider.bloomfilter.capacity=1000000
spider.bloomfilter.error-rate=0.0001

# === Jackson 序列化 ===
spring.jackson.date-format=yyyy-MM-dd HH:mm:ss
spring.jackson.time-zone=GMT+8
spring.jackson.serialization.fail_on_empty_beans=false

# === 邮件通知配置（可选，不使用通知功能可删除）===
spring.mail.protocol=smtp
spring.mail.host=内网邮件服务器地址
spring.mail.port=465
spring.mail.username=发件邮箱
spring.mail.password=邮箱密码
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

# === Selenium 插件配置（可选，不使用可删除或注释）===
# 注意：WebDriver 版本必须与浏览器版本匹配
# ChromeDriver 下载（Chrome 115+）：https://googlechromelabs.github.io/chrome-for-testing/
# ChromeDriver 下载（Chrome ≤114）：https://registry.npmmirror.com/-/binary/chromedriver/
# GeckoDriver 下载：https://github.com/mozilla/geckodriver/releases
# selenium.driver.chrome=/opt/driver/chromedriver
# selenium.driver.firefox=/opt/driver/geckodriver

# === Druid 连接池配置（可选，使用默认值即可）===
# spring.datasource.druid.initial-size=5
# spring.datasource.druid.max-active=20
# spring.datasource.druid.min-idle=5
# spring.datasource.druid.max-wait=60000

# === 健康检查配置（可选，用于运维监控）===
# management.endpoints.web.exposure.include=health,info
# management.endpoint.health.show-details=always

# === 自动配置排除 ===
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.data.mongo.MongoDataAutoConfiguration,org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration
```

### 4.3 关键配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `server.port` | 8088 | Web 服务端口 |
| `spring.datasource.url` | - | MySQL 连接地址，必须修改 |
| `spring.datasource.username` | root | MySQL 用户名 |
| `spring.datasource.password` | - | MySQL 密码，必须修改 |
| `spider.thread.max` | 64 | 平台全局最大线程数 |
| `spider.thread.default` | 8 | 单任务默认线程数 |
| `spider.job.enable` | true | 定时任务开关，`true` 才能执行 Cron 任务，设为 `false` 可关闭定时任务 |
| `spider.workspace` | /data/spider | 日志和历史版本存储目录 |
| `spider.bloomfilter.capacity` | 1000000 | URL 去重布隆过滤器容量 |
| `spider.bloomfilter.error-rate` | 0.0001 | 布隆过滤器容错率 |

---

## 5. 启动与验证

### 5.1 启动服务

**Linux（前台运行，用于测试）：**

```bash
cd /opt/spider-flow
java -jar spider-flow.jar
```

**Linux（后台运行）：**

```bash
cd /opt/spider-flow
nohup java -jar spider-flow.jar > app.log 2>&1 &
echo $! > app.pid
```

**Linux（Systemd 服务，推荐生产环境）：**

创建 `/etc/systemd/system/spider-flow.service`：

```ini
[Unit]
Description=Spider Flow Service
After=network.target mysqld.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/spider-flow
EnvironmentFile=-/etc/sysconfig/spider-flow
ExecStart=/usr/local/jdk1.8.0_XXX/bin/java $JAVA_OPTS -jar spider-flow.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> ⚠️ 请将 `jdk1.8.0_XXX` 替换为实际安装的 JDK 目录名，可通过 `ls /usr/local/` 查看。
>
> `After=mysqld.service` 中的服务名取决于 MySQL 安装方式：二进制安装通常为 `mysqld.service`，yum/apt 包安装可能为 `mysql.service` 或 `mariadb.service`，可通过 `systemctl list-units | grep -i mysql` 确认。如果 MySQL 在其他服务器上，可删除此依赖。
>
> 可选：创建 `/etc/sysconfig/spider-flow` 文件定义 JVM 参数，例如 `JAVA_OPTS="-Xms1g -Xmx2g -XX:+UseG1GC"`，无需修改 service 文件即可调整内存配置。

```bash
# 启用并启动服务
systemctl daemon-reload
systemctl enable spider-flow
systemctl start spider-flow

# 查看状态
systemctl status spider-flow

# 查看日志
journalctl -u spider-flow -f
```

**Windows（前台运行）：**

```powershell
cd C:\opt\spider-flow
java -jar spider-flow.jar
```

**Windows（后台运行）：**

```powershell
Start-Process -FilePath "java" -ArgumentList "-jar spider-flow.jar" -RedirectStandardOutput "app.log" -RedirectStandardError "error.log" -NoNewWindow
```

### 5.2 验证部署

1. **检查进程是否启动：**

```bash
# Linux
ps aux | grep spider-flow
tail -f /opt/spider-flow/app.log

# Windows
Get-Process java
Get-Content app.log -Wait
```

2. **检查端口是否监听：**

```bash
# Linux
netstat -tlnp | grep 8088
# 或
ss -tlnp | grep 8088

# Windows
netstat -ano | findstr 8088
```

3. **访问 Web 界面：**

```
http://内网服务器IP:8088
```

正常情况下应看到 spider-flow 的可视化流程编辑器界面。

4. **验证数据库连接：**

登录后尝试创建一个简单的爬虫流程并保存，如果保存成功则说明数据库连接正常。

5. **检查应用健康状态（可选）：**

> ⚠️ 健康检查端点需要 `spring-boot-starter-actuator` 依赖，当前项目默认未包含。如需使用，请先在 `spider-flow-web/pom.xml` 中添加依赖：
> ```xml
> <dependency>
>     <groupId>org.springframework.boot</groupId>
>     <artifactId>spring-boot-starter-actuator</artifactId>
> </dependency>
> ```
> 添加后重新编译打包，再配置以下属性即可启用。

```properties
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=always
```

可访问 `http://IP:8088/actuator/health` 查看应用状态。

### 5.3 日志排查

```bash
# 实时查看日志
tail -f app.log

# 查看最后 100 行
tail -100 app.log

# 实时查看并过滤错误
tail -f app.log | grep -i error

# 查看特定时间段的日志
grep "2024-01-01" app.log

# 查看内存溢出等 JVM 错误
grep -i "OutOfMemoryError\|StackOverflowError" app.log
```

---

## 6. 常见问题

### 6.1 启动报错：`Communications link failure`

**原因：** 无法连接 MySQL 数据库

**解决：**
- 检查 MySQL 服务是否启动
- 检查 `application.properties` 中的数据库地址、端口、用户名、密码
- 检查防火墙是否放行 3306 端口
- 检查 MySQL 是否允许远程连接

```bash
# 检查 MySQL 连接
mysql -h 数据库地址 -P 3306 -u root -p

# 如果是远程连接，需要授权：
mysql -u root -p

# MySQL 5.7 语法：
GRANT ALL PRIVILEGES ON spiderflow.* TO 'root'@'%' IDENTIFIED BY '密码';
FLUSH PRIVILEGES;

# MySQL 8.0+ 语法（IDENTIFIED BY 已移除，需分两步）：
# CREATE USER 'root'@'%' IDENTIFIED BY '密码';
# GRANT ALL PRIVILEGES ON spiderflow.* TO 'root'@'%';
# FLUSH PRIVILEGES;
```

### 6.2 启动报错：`Table 'spiderflow.xxx' doesn't exist`

**原因：** 数据库未初始化

**解决：**
```bash
mysql -u root -p < spiderflow.sql
```

### 6.3 端口被占用

**现象：** 启动时报错 `Web server failed to start. Port 8088 was already in use.` 或类似信息。

**排查思路：** 先确认占用端口的是什么进程，再决定是**停掉占用进程**还是**更换 spider-flow 端口**。

#### 第一步：查看占用端口的进程

**Linux：**

```bash
# 方式一：lsof（推荐，信息最全）
lsof -i:8088
# 输出示例：
# COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# java     1234 root   52u  IPv6 45678      0t0  TCP *:8088 (LISTEN)

# 方式二：ss（系统自带，无需额外安装）
ss -tlnp | grep 8088

# 方式三：netstat
netstat -tlnp | grep 8088
```

**Windows（PowerShell）：**

```powershell
# 方式一：Get-NetTCPConnection（推荐）
Get-NetTCPConnection -LocalPort 8088 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, OwningProcess, State |
    Format-Table -AutoSize

# 方式二：netstat
netstat -ano | findstr :8088

# 查看 PID 对应的进程名
Get-Process -Id <PID>
```

#### 第二步：判断并处理

确认占用进程后，根据情况选择处理方式：

**情况 A：占用进程是旧的 spider-flow 实例 → 停掉旧实例**

```bash
# Linux
kill <PID>                # 优雅停止，推荐先试
kill -9 <PID>             # 强制停止，优雅停止无效时使用

# 如果使用 systemd 管理
systemctl stop spider-flow

# Windows（PowerShell）
Stop-Process -Id <PID> -Force

# Windows 也推荐按附录 C 的方式停止
```

**情况 B：占用进程是其他服务且不能停 → 更换 spider-flow 端口**

在 JAR 包同目录的 `application.properties` 中修改端口：

```properties
# 将 8088 改为其他未被占用的端口，例如 18088、9090 等
server.port=18088
```

或者通过启动参数临时指定端口：

```bash
# Linux
java -jar spider-flow.jar --server.port=18088

# Windows
java -jar spider-flow.jar --server.port=18088
```

> ⚠️ 更换端口后需同步更新：
> 1. **防火墙规则**：放行新端口（参见 [6.6 防火墙配置](#66-防火墙配置)）
> 2. **访问地址**：浏览器使用 `http://IP:新端口` 访问
> 3. **如果有反向代理**（如 Nginx）：同步修改 `proxy_pass` 中的端口

#### 第三步：验证端口已释放

```bash
# Linux - 确认端口不再被占用
ss -tlnp | grep 8088

# Windows
Get-NetTCPConnection -LocalPort 8088 -ErrorAction SilentlyContinue
```

确认无输出后即可重新启动 spider-flow。

### 6.4 内存不足

**解决：** 调整 JVM 内存参数

```bash
java -Xms512m -Xmx2g -jar spider-flow.jar
```

| 参数 | 说明 |
|------|------|
| `-Xms512m` | 初始堆内存 |
| `-Xmx2g` | 最大堆内存 |

### 6.5 中文乱码

**解决：** 确保 MySQL 使用 UTF-8 编码

```sql
-- 检查数据库编码
SHOW CREATE DATABASE spiderflow;

-- 检查表编码
SHOW CREATE TABLE sp_flow;

-- 如果不是 utf8mb4，修改数据库默认字符集（仅影响新建表）：
ALTER DATABASE spiderflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 如果已有表也需要修改字符集（逐表执行）：
ALTER TABLE sp_flow CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sp_datasource CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sp_function CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sp_variable CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sp_task CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE sp_flow_notice CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6.6 防火墙配置

```bash
# CentOS 7+ 开放端口
firewall-cmd --zone=public --add-port=8088/tcp --permanent
firewall-cmd --reload

# Ubuntu/Debian
ufw allow 8088/tcp

# Windows
netsh advfirewall firewall add rule name="SpiderFlow" dir=in action=allow protocol=TCP localport=8088
```

### 6.7 Selenium WebDriver 报错

**原因：** WebDriver 版本与浏览器版本不匹配，或 WebDriver 文件路径配置错误

**解决：**
1. 检查服务器上 Chrome/Firefox 的版本
2. 下载对应版本的 WebDriver
3. 确保 `application.properties` 中的路径正确
4. 确保 WebDriver 文件有执行权限：`chmod +x /opt/driver/chromedriver`

---

## 附录

### 附录 A：完整部署清单

```
部署前检查：
□ JDK 8 已安装，java -version 正常
□ MySQL 5.7+ 已安装并启动
□ spiderflow.sql 已导入（脚本会自动创建数据库）
□ /data/spider 目录已创建（Linux）或 C:\data\spider（Windows）
□ application.properties 已配置数据库连接
□ 防火墙已开放 8088 端口

部署步骤：
□ 上传 spider-flow.jar 到服务器
□ 创建 application.properties 配置文件
□ 启动服务：java -jar spider-flow.jar
□ 访问 http://IP:8088 验证
□ 创建测试流程验证功能正常
```

---

### 附录 B：目录结构参考

```
/opt/spider-flow/
├── spider-flow.jar           # 主程序
├── application.properties    # 配置文件（外部，可选）
├── app.log                   # 运行日志
├── app.pid                   # 进程 ID（可选）
├── spiderflow.sql            # 数据库脚本（部署用，可删除）
└── driver/                   # WebDriver 目录（可选）
    ├── chromedriver
    └── geckodriver

/data/spider/                 # 工作目录（配置文件中 spider.workspace 指定）
├── logs/                     # 任务执行日志
└── history/                  # 流程历史版本
```

---

### 附录 C：停止服务

```bash
# Linux 方式一：杀进程
kill $(cat /opt/spider-flow/app.pid)

# Linux 方式二：查找并杀进程
ps aux | grep spider-flow
kill <PID>

# Linux 方式三：Systemd
systemctl stop spider-flow

# Windows 方式一：按端口查找并杀进程（推荐）
$pid = (Get-NetTCPConnection -LocalPort 8088).OwningProcess
Stop-Process -Id $pid

# Windows 方式二：使用任务管理器
# 打开任务管理器 -> 找到 java 进程 -> 结束任务
```

> ⚠️ Windows 上避免使用 `Stop-Process -Name java`，该命令会杀掉所有 Java 进程。

---

### 附录 D：JDBC URL 参数说明

配置文件中 `spring.datasource.url` 的参数说明：

| 参数 | 值 | 说明 |
|------|-----|------|
| `useSSL` | false | 是否使用 SSL 连接，内网环境通常设为 false |
| `useUnicode` | true | 是否使用 Unicode 字符集 |
| `characterEncoding` | UTF8 | 字符编码，必须为 UTF8（不是 utf-8） |
| `autoReconnect` | true | 连接断开时是否自动重连 |
| `allowPublicKeyRetrieval` | true | 允许客户端从服务器获取公钥，MySQL 8.0 + connector 8.x 环境必需，缺少会导致 `Public Key Retrieval is not allowed` 错误 |

完整 URL 格式：
```
jdbc:mysql://主机:端口/数据库名?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true
```

---

### 附录 E：数据备份

#### 数据库备份

```bash
# 备份数据库
mysqldump -u root -p spiderflow > spiderflow_backup_$(date +%Y%m%d).sql

# 定时备份（添加到 crontab，每天凌晨 2 点执行）
0 2 * * * mysqldump -u root -p密码 spiderflow > /backup/spiderflow_$(date +\%Y\%m\%d).sql
```

#### 工作目录备份

```bash
# 备份日志和历史版本
tar -czf spider_workspace_$(date +%Y%m%d).tar.gz /data/spider/
```

#### 数据库恢复

```bash
# 恢复数据库
mysql -u root -p spiderflow < spiderflow_backup_20240101.sql
```

---

### 附录 F：生产环境 JVM 参数建议

```bash
java -Xms1g -Xmx2g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/opt/spider-flow/heapdump.hprof \
     -jar spider-flow.jar
```

| 参数 | 说明 |
|------|------|
| `-Xms1g` | 初始堆内存 |
| `-Xmx2g` | 最大堆内存 |
| `-XX:+UseG1GC` | 使用 G1 垃圾收集器 |
| `-XX:MaxGCPauseMillis=200` | GC 最大暂停时间 200ms |
| `-XX:+HeapDumpOnOutOfMemoryError` | OOM 时自动生成堆转储 |
| `-XX:HeapDumpPath` | 堆转储文件路径 |

---

**部署完成！** 访问 `http://内网服务器IP:8088` 即可使用 spider-flow 可视化爬虫平台。

---

## 附录 G：Docker 部署（支持浏览器自动化 + ARM64）

> Docker 部署方式内置 Chrome for Testing 浏览器（amd64 / arm64 统一方案）+ ChromeDriver，支持 Selenium 浏览器自动化爬取。

### G.1 环境要求

| 项目 | 要求 |
|------|------|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |
| 磁盘空间 | ≥ 4 GB（应用镜像约 1.2 GB + MySQL 8.0 镜像约 550 MB + 运行数据） |
| 共享内存 | ≥ 2 GB（Chrome 运行需要） |

### G.2 离线准备（在外网机器完成）

**构建 Docker 镜像：**

```bash
# 1. 编译 JAR 包
mvn clean package -DskipTests

# 2. 构建镜像 + 导出（根据内网服务器架构选择命令）

# --- 如果内网是 x86_64（常见）---
docker build -t spider-flow:latest .
docker pull mysql:8.0
docker save spider-flow:latest -o spider-flow.tar
docker save mysql:8.0 -o mysql-8.0.tar

# --- 如果内网是 ARM64（如银河麒麟 + 飞腾/鲲鹏处理器）---
# Docker Desktop + WSL2 下通过 QEMU 模拟构建，无需 buildx / containerd
docker build --platform linux/arm64 -t spider-flow:arm64 .
docker tag spider-flow:arm64 spider-flow:latest
# 拉取 ARM64 版本的 MySQL 镜像（默认拉取的是 amd64，必须显式指定 --platform）
docker pull --platform linux/arm64 mysql:8.0
docker save spider-flow:latest -o spider-flow.tar
docker save mysql:8.0 -o mysql-8.0.tar
```

> **如何判断内网架构？** 在内网服务器上执行 `uname -m`：
> - 输出 `x86_64` → 使用 x86_64 构建命令
> - 输出 `aarch64` → 使用 ARM64 构建命令
>
> **ARM64 构建说明：** `docker build --platform linux/arm64` 通过 Docker Desktop 内置的 QEMU 模拟 ARM64 环境完成构建，产出的镜像天然就是 ARM64 单架构，可直接 `docker save / docker load`，无需启用 containerd 镜像存储或配置 buildx builder。构建速度比原生慢约 3-5 倍，但流程更简单可靠。
>
> **Chrome for Testing 说明：** 镜像使用 Google 官方的 Chrome for Testing 独立二进制包（同时支持 amd64 和 arm64），Chrome 与 ChromeDriver 版本自动匹配，无需混入第三方系统仓库，构建过程更稳定可靠。
>
> ⚠️ **MySQL 镜像架构必须匹配：** `docker pull mysql:8.0` 默认拉取当前主机架构（Windows 上是 amd64）的镜像。如果内网是 ARM64，**必须**使用 `docker pull --platform linux/arm64 mysql:8.0` 拉取 ARM64 版本，否则 `docker load` 后容器也无法运行。

**传输到内网服务器的文件（保持目录结构）：**

```
deploy-dir/
├── spider-flow.tar        # 应用镜像
├── mysql-8.0.tar          # MySQL 镜像
├── docker-compose.yml     # 编排文件
├── .env.example           # 环境变量模板
└── db/
    └── spiderflow.sql     # 数据库初始化脚本（docker-compose.yml 通过 ./db/spiderflow.sql 挂载）
```

> 注：entrypoint.sh 已在 docker build 时打包进镜像，无需单独传输。

> **Windows（PowerShell）用户：** 以上 `docker` 命令在 PowerShell 中同样适用。确保 Docker Desktop 已切换到 **Linux 容器模式**（右上角菜单 → Switch to Linux containers）。

### G.3 部署步骤

```bash
# 1. 在内网服务器上导入镜像
docker load -i spider-flow.tar
docker load -i mysql-8.0.tar

# 2. 复制配置文件
cp .env.example .env

# 3. 编辑 .env 文件，修改 MySQL 密码和端口
#    MYSQL_ROOT_PASSWORD=你的密码
#    APP_PORT=8088

# 4. 启动服务
docker compose up -d

# 5. 查看运行状态
docker compose ps

# 6. 查看日志
docker compose logs -f app
```

### G.4 镜像说明

Dockerfile 基于 `eclipse-temurin:8-jre-jammy`（同时支持 amd64 和 arm64），内置：

| 组件 | amd64 (x86_64) | arm64 (aarch64 麒麟) |
|------|----------------|----------------------|
| 浏览器 | Chrome for Testing（Google 官方） | Chrome for Testing（Google 官方） |
| ChromeDriver | 与 Chrome 版本自动匹配 | 与 Chrome 版本自动匹配 |
| JRE 8 | ✅ | ✅ |
| 中文字体 | ✅ 文泉驿 + Noto CJK | ✅ 文泉驿 + Noto CJK |

> **Chrome for Testing** 是 Google 官方为自动化测试提供的独立 Chrome 二进制包，同时支持 amd64 和 arm64 Linux，Chrome 与 ChromeDriver 版本自动匹配，无需混入第三方系统仓库。

MySQL 使用 `mysql:8.0` 官方镜像，通过 `--default-authentication-plugin=mysql_native_password` 保持与项目内置 MySQL Connector/J 5.x 驱动的兼容性。

Docker Compose 使用 `spider-net` bridge 网络，`app` 和 `mysql` 两个容器通过该网络通信，容器间使用服务名 `mysql` 作为数据库主机名。

### G.5 关键配置

**Chrome 在 Docker 中运行的注意事项：**

| 配置 | 说明 |
|------|------|
| `--shm-size=2g` | Chrome 需要较大共享内存，否则会崩溃 |
| `--no-sandbox` | Chrome 沙箱需要特定内核权限（如 CAP_SYS_ADMIN），容器默认不具备。Selenium 节点默认不勾选"沙盒模式"即由代码自动添加 `--no-sandbox`，无需手动操作 |
| `--disable-dev-shm-usage` | 让 Chrome 使用 `/tmp` 而非 `/dev/shm` 做共享内存，避免容器内 `/dev/shm` 不足导致 tab 崩溃（page crash）。已由代码自动添加，**无需在节点参数中手动配置** |
| `headless` 模式 | Docker 无 GUI，Selenium 节点需勾选"无头模式" |
| 中文字体 | 镜像已内置，中文网页正常显示 |

**JVM 参数调整：**

Docker 镜像默认 JVM 参数为 `-Xms512m -Xmx2g -XX:+UseG1GC`，可通过 `.env` 文件覆盖 `JAVA_OPTS` 变量来调整：

```properties
# .env 文件中取消注释并修改（默认已包含注释行）
JAVA_OPTS=-Xms1g -Xmx4g -XX:+UseG1GC
```

**Selenium 节点使用：**

在 spider-flow 编辑器中使用 Selenium 节点时：
1. 浏览器类型选择 `chrome`
2. 勾选 `headless`（无头模式）
3. ChromeDriver 路径使用默认值 `/usr/local/bin/chromedriver`（已通过环境变量注入）

> **无需手动添加启动参数**：`--no-sandbox` 与 `--disable-dev-shm-usage` 已由后端代码自动注入到 Chrome 启动参数中，确保容器环境下稳定运行。如需禁用其他功能（如禁用图片、隐身模式等），仍可在节点"其他参数"中按需添加。

### G.6 常用命令

```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 重启
docker compose restart app

# 查看日志
docker compose logs -f app

# 进入容器调试
docker exec -it spider-flow-app bash

# 检查浏览器是否正常（Chrome for Testing，通过符号链接 google-chrome-stable 访问）
docker exec spider-flow-app google-chrome-stable --version
docker exec spider-flow-app chromedriver --version

# 备份数据库（在 mysql 容器中执行，app 容器没有 MySQL 客户端）
docker exec spider-flow-mysql mysqldump -u root -p spiderflow > backup.sql

# 恢复数据库
docker exec -i spider-flow-mysql mysql -u root -p spiderflow < backup.sql

# 查看网络（容器间通过 spider-net bridge 网络通信）
# 网络名格式为 <项目目录名>_spider-net，默认为 spider-flow_spider-net
docker network ls | grep spider
docker network inspect spider-flow_spider-net
```

### G.7 数据持久化

| 数据卷 | 容器路径 | 说明 |
|--------|----------|------|
| `mysql-data` | `/var/lib/mysql` | MySQL 数据文件 |
| `spider-workspace` | `/data/spider` | 爬虫日志和历史版本 |

```bash
# 查看数据卷
docker volume ls | grep spider

# 备份数据卷（卷名格式为 <项目目录名>_<卷名>，默认为 spider-flow_mysql-data）
# 如果 docker-compose.yml 所在目录不是 spider-flow，请用 docker volume ls 查看实际卷名
docker run --rm -v spider-flow_mysql-data:/data -v $(pwd):/backup alpine \
    tar czf /backup/mysql-data-backup.tar.gz -C /data .
```

### G.8 内网离线部署完整清单

```
需传输到内网的文件（保持目录结构）：
□ spider-flow.tar              # 应用 Docker 镜像（注意架构：amd64 或 arm64）
□ mysql-8.0.tar                # MySQL Docker 镜像（mysql:8.0 同时支持 amd64 和 arm64）
□ docker-compose.yml           # Docker Compose 编排文件
□ .env.example                 # 环境变量模板
□ db/spiderflow.sql            # 数据库初始化脚本（必须在 db/ 子目录中）

目录结构：
  deploy-dir/
  ├── docker-compose.yml
  ├── .env.example
  ├── spider-flow.tar
  ├── mysql-8.0.tar
  └── db/
      └── spiderflow.sql       # docker-compose.yml 通过 ./db/spiderflow.sql 挂载

部署步骤：
□ 确认内网架构：uname -m（x86_64 或 aarch64）
□ 确保 spider-flow.tar 与内网架构匹配
□ 确保 mysql-8.0.tar 与内网架构匹配（ARM64 必须用 docker pull --platform linux/arm64 拉取）
□ 导入镜像：docker load -i spider-flow.tar; docker load -i mysql-8.0.tar
□ 配置环境变量：cp .env.example .env && 编辑 .env
□ 启动服务：docker compose up -d
□ 验证：docker compose ps（两个容器均 healthy）
□ 访问：http://内网服务器IP:8088
```
