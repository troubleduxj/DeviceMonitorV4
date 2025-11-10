# Mock功能快速安装指南

## 🎯 5分钟完成安装

### Step 1: 创建数据库表 (1分钟)

```bash
# 方式1: psql命令
psql -U postgres -d device_monitor -f database/migrations/add_mock_data_table.sql
psql -U postgres -d device_monitor -f database/migrations/add_mock_management_menu.sql

# 方式2: 进入psql后执行
psql -U postgres -d device_monitor
\i database/migrations/add_mock_data_table.sql
\i database/migrations/add_mock_management_menu.sql
\q
```

### Step 2: 重启后端 (1分钟)

```bash
cd D:\Cursor\Project\DeviceMonitorV2_20251013_V1\DeviceMonitorV2
python run.py
```

### Step 3: 初始化权限 (1分钟)

1. 打开浏览器，访问系统
2. 按F12打开控制台
3. 执行以下代码：

```javascript
const token = localStorage.getItem('access_token');
fetch('/api/v2/system/init-button-permissions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => {
  console.log(data);
  alert(`完成！创建 ${data.data.created} 个按钮权限`);
  location.reload();  // 刷新页面
});
```

### Step 4: 访问Mock管理 (1分钟)

刷新页面后，在左侧菜单找到：**Mock数据管理**

### Step 5: 创建第一个Mock规则 (1分钟)

1. 点击"新建Mock规则"
2. 填写：
   - 规则名称：`测试Mock`
   - HTTP方法：`GET`
   - URL匹配模式：`/api/v2/test-mock`
   - 响应数据：
   ```json
   {
     "code": 200,
     "message": "Mock测试成功！",
     "data": {
       "hello": "Mock World"
     }
   }
   ```
3. 点击确定

### Step 6: 测试Mock (1分钟)

在浏览器控制台测试：

```javascript
// 启用Mock
window.__mockInterceptor.enable()

// 测试请求
fetch('/api/v2/test-mock')
  .then(res => res.json())
  .then(data => {
    console.log('Mock响应:', data);
    alert('Mock测试成功！\n' + JSON.stringify(data, null, 2));
  });
```

## ✅ 安装完成！

现在您可以：

1. **创建更多Mock规则** - 模拟各种API响应
2. **启用/禁用Mock** - 灵活切换真实/Mock数据
3. **查看详细使用指南** - [Mock数据管理完整文档](./MOCK_DATA_GUIDE.md)

## 🔧 常用命令

```javascript
// 启用Mock
window.__mockInterceptor.enable()

// 禁用Mock
window.__mockInterceptor.disable()

// 查看Mock状态
window.__mockInterceptor.getStats()

// 重新加载规则
window.__mockInterceptor.reload()
```

## 📚 下一步

- 阅读[完整使用指南](./MOCK_DATA_GUIDE.md)
- 查看[使用场景示例](./MOCK_DATA_GUIDE.md#-使用场景示例)
- 了解[高级用法](./MOCK_DATA_GUIDE.md#-高级用法)

