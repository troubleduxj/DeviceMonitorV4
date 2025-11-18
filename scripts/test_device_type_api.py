"""
测试设备类型 API 是否返回 icon 字段
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:3001"

def test_device_types_api():
    """测试设备类型列表 API"""
    try:
        print("测试设备类型列表 API...")
        url = f"{BASE_URL}/api/v2/devices/types"
        params = {
            'page': 1,
            'page_size': 10
        }
        
        response = requests.get(url, params=params)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API 调用成功！")
            print(f"\n返回数据结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查是否包含 icon 字段
            if data.get('data') and len(data['data']) > 0:
                first_item = data['data'][0]
                if 'icon' in first_item:
                    print(f"\n✅ icon 字段存在！")
                    print(f"第一条记录的图标: {first_item.get('icon')}")
                else:
                    print(f"\n❌ icon 字段不存在！")
                    print(f"可用字段: {list(first_item.keys())}")
        else:
            print(f"\n❌ API 调用失败！")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务正在运行")
        print("提示: 请在另一个终端运行 'python main.py' 启动后端服务")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_device_types_api()
