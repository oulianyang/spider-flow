# ============================================================
# spider-flow Docker 镜像（内置浏览器 + ChromeDriver）
# ============================================================
# 支持架构: amd64 (x86_64), arm64 (aarch64)
# 浏览器方案: Chrome for Testing（Google 官方独立二进制包，双架构统一）
#
# 构建前请先执行: mvn clean package -DskipTests
#
# 构建命令（当前架构）:
#   docker build -t spider-flow:latest .
#
# 交叉构建 ARM64 镜像（Windows 上，需要 Docker Desktop + WSL2）:
#   docker build --platform linux/arm64 -t spider-flow:arm64 .
#   docker tag spider-flow:arm64 spider-flow:latest
#
# 导出镜像（离线部署用）:
#   docker save spider-flow:latest -o spider-flow.tar
#   docker pull mysql:8.0                              # x86_64
#   docker pull --platform linux/arm64 mysql:8.0        # ARM64（必须指定平台）
#   docker save mysql:8.0 -o mysql-8.0.tar
#
# 运行命令: docker run -d -p 8088:8088 --shm-size=2g spider-flow
# ============================================================

FROM eclipse-temurin:8-jre-jammy

LABEL maintainer="spider-flow"
LABEL description="spider-flow visual web scraping platform with browser automation"

# ========== 安装浏览器 + ChromeDriver + 中文字体 ==========
ENV DEBIAN_FRONTEND=noninteractive

# --- 公共依赖（amd64 和 arm64 共用）---
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    # 中文字体（解决中文网页乱码）
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    # Chrome 需要的共享库
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && \
    # ========= Chrome for Testing（amd64 / arm64 统一方案） =========
    # 使用 Google 官方的 Chrome for Testing 独立二进制包
    # 优点：Chrome 与 ChromeDriver 版本自动匹配，无需混入第三方仓库，双架构统一
    # 通过 uname -m 检测运行时架构，不依赖 BuildKit 注入的 TARGETARCH，
    # 避免在未启用 BuildKit 时 TARGETARCH 为空导致 x86 机器错误下载 arm64 包
    case "$(uname -m)" in \
        x86_64)  PLATFORM="linux64" ;; \
        aarch64) PLATFORM="linux-arm64" ;; \
        *) echo "不支持的 CPU 架构: $(uname -m)"; exit 1 ;; \
    esac && \
    echo "=== Installing Chrome for Testing (${PLATFORM}) ===" && \
    VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") && \
    echo "Chrome for Testing version: ${VERSION}" && \
    # 下载 Chrome
    curl -sS -o /tmp/chrome.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/${PLATFORM}/chrome-${PLATFORM}.zip" && \
    unzip -q /tmp/chrome.zip -d /tmp/ && \
    mv /tmp/chrome-${PLATFORM} /opt/chrome && \
    ln -sf /opt/chrome/chrome /usr/local/bin/google-chrome-stable && \
    chmod +x /opt/chrome/chrome && \
    # 下载 ChromeDriver（版本与 Chrome 完全匹配）
    curl -sS -o /tmp/chromedriver.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/${PLATFORM}/chromedriver-${PLATFORM}.zip" && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-${PLATFORM}/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    # 清理
    rm -rf /tmp/chrome* /tmp/chromedriver* /var/lib/apt/lists/*

# ========== 应用配置 ==========
ENV SERVER_PORT=8088 \
    SPRING_DATASOURCE_URL="jdbc:mysql://mysql:3306/spiderflow?useSSL=false&useUnicode=true&characterEncoding=UTF8&autoReconnect=true&allowPublicKeyRetrieval=true" \
    SPRING_DATASOURCE_USERNAME=root \
    SPRING_DATASOURCE_PASSWORD=spiderflow \
    SPIDER_WORKSPACE=/data/spider \
    SPIDER_JOB_ENABLE=true \
    SPIDER_THREAD_MAX=64 \
    SPIDER_THREAD_DEFAULT=8 \
    SELENIUM_DRIVER_CHROME=/usr/local/bin/chromedriver

# 创建工作目录
RUN mkdir -p /data/spider /app

WORKDIR /app

# 复制 JAR 包和启动脚本（需先 mvn package）
COPY spider-flow-web/target/spider-flow.jar ./spider-flow.jar
COPY entrypoint.sh ./entrypoint.sh
# 修复 Windows 换行符（CRLF → LF）并设置执行权限
RUN sed -i 's/\r$//' ./entrypoint.sh && chmod +x ./entrypoint.sh

# 暴露端口
EXPOSE 8088

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8088/ || exit 1

# JVM 参数可通过 JAVA_OPTS 环境变量覆盖
ENV JAVA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -Djava.security.egd=file:/dev/./urandom"

# 使用 entrypoint.sh 启动（确保 -D 参数在 -jar 之前）
ENTRYPOINT ["./entrypoint.sh"]
