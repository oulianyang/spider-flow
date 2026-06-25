#!/bin/sh
# ============================================================
# spider-flow Docker Entrypoint
# ============================================================
# Java 命令格式: java [JVM选项] -jar app.jar [应用参数]
# -D 系统属性必须放在 -jar 之前才能被 JVM 识别
# ============================================================

# 关键环境变量校验：数据源配置缺失会导致启动后连接失败，错误信息隐蔽，故前置 fail-fast
if [ -z "${SPRING_DATASOURCE_URL}" ]; then
    echo "ERROR: 环境变量 SPRING_DATASOURCE_URL 未设置，无法连接数据库，请通过 -e 或 docker-compose 配置" >&2
    exit 1
fi
if [ -z "${SPRING_DATASOURCE_PASSWORD}" ]; then
    echo "ERROR: 环境变量 SPRING_DATASOURCE_PASSWORD 未设置，请通过 -e 或 docker-compose 配置（即使密码为空也请显式传入空串）" >&2
    exit 1
fi

exec java \
    ${JAVA_OPTS} \
    -Dserver.port="${SERVER_PORT:-8088}" \
    -Dspring.datasource.url="${SPRING_DATASOURCE_URL}" \
    -Dspring.datasource.username="${SPRING_DATASOURCE_USERNAME:-root}" \
    -Dspring.datasource.password="${SPRING_DATASOURCE_PASSWORD}" \
    -Dspider.workspace="${SPIDER_WORKSPACE:-/data/spider}" \
    -Dspider.job.enable="${SPIDER_JOB_ENABLE:-true}" \
    -Dspider.thread.max="${SPIDER_THREAD_MAX:-64}" \
    -Dspider.thread.default="${SPIDER_THREAD_DEFAULT:-8}" \
    -Dselenium.driver.chrome="${SELENIUM_DRIVER_CHROME:-/usr/local/bin/chromedriver}" \
    -jar spider-flow.jar
