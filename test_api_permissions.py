"""
通过HTTP请求测试角色权限更新API
"""
import requests
import json

# API配置
BASE_URL = "http://127.0.0.1:8001/api/v2"
ROLE_ID = 3

# 测试数据
test_data = {
    "menu_ids": [1, 2, 3],
    "sys_api_ids": [1, 2, 3],
    "action": "replace"
}

print("=" * 80)
print("测试角色权限更新API")
print("=" * 80)

# 首先需要登录获取token
print("\n1. 登录获取token...")
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   状态码: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('data', {}).get('access_token')
        if token:
            print(f"   ✓ 登录成功，获取到token")
        else:
            print(f"   ✗ 登录响应中没有token")
            print(f"   响应: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
            exit(1)
    else:
        print(f"   ✗ 登录失败")
        print(f"   响应: {login_response.text}")
        exit(1)
        
except Exception as e:
    print(f"   ✗ 登录请求失败: {e}")
    exit(1)

# 测试更新权限API
print(f"\n2. 更新角色 {ROLE_ID} 的权限...")
print(f"   请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    update_response = requests.put(
        f"{BASE_URL}/roles/{ROLE_ID}/permissions",
        json=test_data,
        headers=headers
    )
    
    print(f"   状态码: {update_response.status_code}")
    print(f"   响应头: {dict(update_response.headers)}")
    
    if update_response.status_code == 200:
        result = update_response.json()
        print(f"   ✓ 更新成功")
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"   ✗ 更新失败")
        print(f"   响应: {update_response.text}")
        
        # 尝试解析JSON错误信息
        try:
            error_data = update_response.json()
            print(f"   错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            pass
            
except Exception as e:
    print(f"   ✗ 更新请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
