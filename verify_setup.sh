#!/bin/bash
# WebProbe 阶段5验证脚本

echo "🚀 WebProbe 阶段5验证开始..."
echo ""

# 检查 .env 文件
echo "📋 步骤 1/4: 检查 .env 文件..."
if [ -f .env ]; then
    echo "   ✅ .env 文件存在"
    echo "   📊 DATABASE_URL: $(grep DATABASE_URL .env | cut -d'@' -f2 | cut -d'/' -f1)"
else
    echo "   ❌ .env 文件不存在"
    exit 1
fi
echo ""

# 测试配置加载
echo "🔧 步骤 2/4: 测试配置加载..."
python -c "from app.config import settings; print('   ✅ 配置加载成功'); print(f'   📊 应用名称: {settings.APP_NAME}'); print(f'   📊 调试模式: {settings.DEBUG}')" 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 配置文件正常"
else
    echo "   ❌ 配置加载失败"
    exit 1
fi
echo ""

# 初始化数据库
echo "🗄️  步骤 3/4: 初始化数据库..."
python scripts/init_db.py 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 数据库初始化成功"
else
    echo "   ❌ 数据库初始化失败"
    echo "   💡 请检查 Render 数据库是否正在运行"
    exit 1
fi
echo ""

# 提示启动服务器
echo "🎯 步骤 4/4: 准备启动 FastAPI 服务器..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 所有前置检查已通过！"
echo ""
echo "📍 下一步：启动 FastAPI 应用"
echo ""
echo "运行以下命令启动服务器："
echo "   uvicorn app.main:app --reload"
echo ""
echo "启动后，在新终端窗口中测试："
echo "   curl http://localhost:8000/"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "或在浏览器中访问："
echo "   http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

