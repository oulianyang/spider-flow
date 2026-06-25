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
#   docker buildx build --platform linux/arm64 -t spider-flow:arm64 --load .
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

# --- 第 1 层：安装公共依赖（字体 + Chrome 运行库）---
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
    && rm -rf /var/lib/apt/lists/*

# --- 第 2 层：下载并安装 Chrome for Testing ---
# 拆分为独立层，避免 QEMU 模拟 ARM64 时单层内存过大被 OOM Killer 杀掉（exit code 9）
# 使用 buildx 原生的 TARGETPLATFORM 变量检测目标架构，兼容经典 builder 和 buildx
RUN case "$(uname -m)" in \
        x86_64)  PLATFORM="linux64" ;; \
        aarch64) PLATFORM="linux-arm64" ;; \
        *) echo "不支持的 CPU 架构: $(uname -m)"; exit 1 ;; \
    esac && \
    echo "=== Installing Chrome for Testing (${PLATFORM}) ===" && \
    VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") && \
    echo "Chrome for Testing version: ${VERSION}" && \
    curl -sS -o /tmp/chrome.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/${PLATFORM}/chrome-${PLATFORM}.zip" && \
    unzip -q /tmp/chrome.zip -d /tmp/ && \
    mv /tmp/chrome-${PLATFORM} /opt/chrome && \
    ln -sf /opt/chrome/chrome /usr/local/bin/google-chrome-stable && \
    chmod +x /opt/chrome/chrome && \
    rm -rf /tmp/chrome*

# --- 第 3 层：下载并安装 ChromeDriver ---
# 单独一层，降低内存峰值；版本与上方 Chrome 自动匹配（同 URL 前缀）
RUN case "$(uname -m)" in \
        x86_64)  PLATFORM="linux64" ;; \
        aarch64) PLATFORM="linux-arm64" ;; \
    esac && \
    VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE") && \
    curl -sS -o /tmp/chromedriver.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/${PLATFORM}/chromedriver-${PLATFORM}.zip" && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-${PLATFORM}/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

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
