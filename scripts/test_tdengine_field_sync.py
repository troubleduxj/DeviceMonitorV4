"""
测试TDengine字段同步功能

使用说明：
1. 确保后端服务正在运行
2. 确保TDengine服务可访问
3. 修改配置参数（如需要）
4. 运行脚本：python scripts/test_tdengine_field_sync.py
"""

import requests
import json
from typing import Dict, Any


# =====================================================
# 配置参数
# =====================================================

# 后端API地址
API_BASE_URL = "http://localhost:8000/api/v2"

# 认证Token（需要先登录获取）
# 如何获取：POST /api/v2/auth/login
AUTH_TOKEN = "YOUR_TOKEN_HERE"

# TDengine配置
TDENGINE_CONFIG = {
    "device_type_code": "welding",          # 设备类型代码
    "tdengine_database": "device_monitor",  # TDengine数据库名
    "tdengine_stable": "weld_data",        # TDengine超级表名
    "server_name": None,                    # TDengine服务器名称（None = 使用默认）
    "field_category": "data_collection"     # 字段分类
}


# =====================================================
# 辅助函数
# =====================================================

def get_headers() -> Dict[str, str]:
    """获取请求头"""
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(response: requests.Response):
    """打印响应结果"""
    try:
        data = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"解析响应失败: {e}")
        print(f"原始响应: {response.text}")


# =====================================================
# 测试函数
# =====================================================

def test_login():
    """测试登录（获取Token）"""
    print_section("步骤1: 登录获取Token")
    
    url = f"{API_BASE_URL}/auth/login"
    payload = {
        "username": "admin",  # 修改为实际用户名
        "password": "admin123"  # 修改为实际密码
    }
    
    response = requests.post(url, json=payload)
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            token = data.get("data", {}).get("access_token")
            print(f"\n✅ 登录成功！Token: {token[:50]}...")
            return token
    
    print("\n❌ 登录失败！请检查用户名和密码")
    return None


def test_preview_fields():
    """测试预览TDengine字段"""
    print_section("步骤2: 预览TDengine字段")
    
    url = f"{API_BASE_URL}/metadata-sync/preview-tdengine-fields"
    params = {
        "device_type_code": TDENGINE_CONFIG["device_type_code"],
        "tdengine_database": TDENGINE_CONFIG["tdengine_database"],
        "tdengine_stable": TDENGINE_CONFIG["tdengine_stable"]
    }
    
    if TDENGINE_CONFIG["server_name"]:
        params["server_name"] = TDENGINE_CONFIG["server_name"]
    
    response = requests.get(url, params=params, headers=get_headers())
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            result = data.get("data", {})
            print(f"\n✅ 预览成功！")
            print(f"   - 总字段数: {result.get('total_fields')}")
            print(f"   - 新建字段: {result.get('new_fields')}")
            print(f"   - 已存在字段: {result.get('existing_fields')}")
            print(f"   - 跳过字段: {result.get('skip_fields')}")
            
            print("\n字段列表:")
            for field in result.get("fields", []):
                status_icon = "🆕" if field["status"] == "new" else "⏭️" if field["status"] == "skip_system" else "✓"
                print(f"  {status_icon} {field['field_code']:20s} | {field['field_type']:10s} | {field['status_text']}")
            
            return True
    
    print("\n❌ 预览失败！")
    return False


def test_sync_fields():
    """测试同步字段"""
    print_section("步骤3: 执行字段同步")
    
    url = f"{API_BASE_URL}/metadata-sync/sync-from-tdengine"
    payload = TDENGINE_CONFIG.copy()
    
    response = requests.post(url, json=payload, headers=get_headers())
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            result = data.get("data", {})
            print(f"\n✅ 同步成功！")
            print(f"   - 总字段数: {result.get('total')}")
            print(f"   - 创建字段: {len(result.get('created', []))}")
            print(f"   - 跳过字段: {len(result.get('skipped', []))}")
            print(f"   - 失败字段: {len(result.get('errors', []))}")
            
            if result.get("created"):
                print("\n已创建字段:")
                for field in result["created"]:
                    print(f"  ✓ {field['field_code']:20s} | ID: {field['id']:5d} | {field['field_name']}")
            
            if result.get("skipped"):
                print("\n跳过字段:")
                for field in result["skipped"]:
                    print(f"  ⏭️ {field['field_code']:20s} | 原因: {field['reason']}")
            
            if result.get("errors"):
                print("\n失败字段:")
                for field in result["errors"]:
                    print(f"  ❌ {field['field_code']:20s} | 错误: {field['error']}")
            
            return True
    
    print("\n❌ 同步失败！")
    return False


def test_get_fields():
    """测试查询已创建的字段"""
    print_section("步骤4: 验证字段已创建")
    
    url = f"{API_BASE_URL}/metadata/fields"
    params = {
        "device_type_code": TDENGINE_CONFIG["device_type_code"],
        "page": 1,
        "page_size": 100
    }
    
    response = requests.get(url, params=params, headers=get_headers())
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            total = data.get("total", 0)
            fields = data.get("data", [])
            print(f"\n✅ 查询成功！共 {total} 个字段")
            
            print("\n字段列表（最近10个）:")
            for field in fields[:10]:
                print(f"  • {field['field_code']:20s} | {field['field_name']:15s} | {field['field_type']:10s}")
            
            return True
    
    print("\n❌ 查询失败！")
    return False


# =====================================================
# 主函数
# =====================================================

def main():
    """主测试流程"""
    print("=" * 60)
    print("  TDengine字段同步功能测试")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"  - API地址: {API_BASE_URL}")
    print(f"  - 设备类型: {TDENGINE_CONFIG['device_type_code']}")
    print(f"  - 数据库: {TDENGINE_CONFIG['tdengine_database']}")
    print(f"  - 超级表: {TDENGINE_CONFIG['tdengine_stable']}")
    
    # 检查Token
    global AUTH_TOKEN
    if AUTH_TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  未配置Token，尝试自动登录...")
        token = test_login()
        if token:
            AUTH_TOKEN = token
        else:
            print("\n❌ 测试中止：无法获取Token")
            return
    
    # 执行测试
    try:
        # 步骤1: 预览字段
        if not test_preview_fields():
            print("\n❌ 测试中止：预览失败")
            return
        
        # 询问是否继续
        print("\n" + "-" * 60)
        confirm = input("是否继续执行同步操作？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消同步")
            return
        
        # 步骤2: 同步字段
        if not test_sync_fields():
            print("\n❌ 测试中止：同步失败")
            return
        
        # 步骤3: 验证结果
        test_get_fields()
        
        print_section("测试完成")
        print("✅ 所有测试步骤已完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

