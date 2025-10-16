#!/bin/bash
# 启动 PostgreSQL 数据库

echo "🚀 启动 PostgreSQL..."

# 检查容器是否已存在
if docker ps -a | grep -q webprobe-postgres; then
    echo "容器已存在，正在启动..."
    docker start webprobe-postgres
else
    echo "创建新容器..."
    docker run -d \
        --name webprobe-postgres \
        -e POSTGRES_USER=webprobe \
        -e POSTGRES_PASSWORD=secret \
        -e POSTGRES_DB=webprobe_db \
        -p 5432:5432 \
        postgres:15-alpine
fi

echo "⏳ 等待 PostgreSQL 启动..."
sleep 5

echo "✅ PostgreSQL 已启动！"
echo "📍 连接信息："
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: webprobe_db"
echo "   User: webprobe"
echo "   Password: secret"

