#!/usr/bin/env python3
"""
测试应用启动
"""
import sys

print("🔧 步骤 1: 测试配置加载...")
try:
    from app.config import settings
    print(f"   ✅ 配置加载成功")
    print(f"   📊 应用名称: {settings.APP_NAME}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    sys.exit(1)

print("\n🔧 步骤 2: 测试模型导入...")
try:
    from app.models import Base, Task, TaskStatus, Result
    print(f"   ✅ 模型导入成功")
except Exception as e:
    print(f"   ❌ 模型导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔧 步骤 3: 测试 Repository 导入...")
try:
    from app.repositories import TaskRepository
    print(f"   ✅ Repository 导入成功")
except Exception as e:
    print(f"   ❌ Repository 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔧 步骤 4: 测试 Schemas 导入...")
try:
    from app.schemas import TaskCreate, TaskResponse, ResultResponse
    print(f"   ✅ Schemas 导入成功")
except Exception as e:
    print(f"   ❌ Schemas 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔧 步骤 5: 测试 FastAPI 应用导入...")
try:
    from app.main import app
    print(f"   ✅ FastAPI 应用导入成功")
    print(f"   📊 应用标题: {app.title}")
except Exception as e:
    print(f"   ❌ FastAPI 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("🎉 所有测试通过！应用可以正常启动")
print("="*50)
print("\n📍 下一步:")
print("   uvicorn app.main:app --reload")
print("\n然后访问:")
print("   http://localhost:8000/docs")

