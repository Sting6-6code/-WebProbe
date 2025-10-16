#!/bin/bash
# 快速验证 FastAPI 应用

echo "🧪 快速验证 WebProbe API..."

# 使用测试环境配置
cp .env.test .env

echo "📊 步骤 1: 初始化数据库..."
python scripts/init_db.py

if [ $? -ne 0 ]; then
    echo "❌ 数据库初始化失败"
    exit 1
fi

echo ""
echo "🚀 步骤 2: 启动 FastAPI 服务器..."
echo "   (按 Ctrl+C 停止服务器)"
echo ""
echo "📍 验证 API:"
echo "   1. 访问 API 文档: http://localhost:8000/docs"
echo "   2. 测试健康检查: curl http://localhost:8000/api/v1/health"
echo "   3. 创建任务: curl -X POST http://localhost:8000/api/v1/tasks -H 'Content-Type: application/json' -d '{\"url\":\"https://example.com\"}'"
echo ""

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

