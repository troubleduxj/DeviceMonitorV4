// 检查测试菜单来源的诊断脚本
console.log('🔍 开始诊断测试菜单来源...\n');

const token = localStorage.getItem('access_token');

if (!token) {
  console.error('❌ 未找到Token');
} else {
  // 获取前端路由
  console.log('1️⃣ 检查前端静态路由...');
  const router = window.__app__?.$router || window.$router;
  if (router) {
    const routes = router.getRoutes();
    const testRoutes = routes.filter(r => 
      r.name && (
        r.name.includes('403') || 
        r.name.includes('404') ||
        r.name.includes('Login') ||
        r.name.includes('Permission') ||
        r.name.includes('Test')
      )
    );
    
    console.log('前端静态路由中的测试页面:');
    console.table(testRoutes.map(r => ({
      name: r.name,
      path: r.path,
      isHidden: r.isHidden,
      meta: r.meta?.title
    })));
  }
  
  // 获取后端菜单
  console.log('\n2️⃣ 检查后端动态菜单...');
  fetch('/api/v2/auth/user/menus', {
    headers: {'Authorization': 'Bearer ' + token}
  })
  .then(res => res.json())
  .then(data => {
    console.log('后端菜单数据获取成功');
    
    // 递归查找测试菜单
    function findTestMenus(menus, parent = '根节点') {
      let result = [];
      (menus || []).forEach(menu => {
        const name = menu.name || menu.title;
        if (name && (
          name.includes('403') ||
          name.includes('404') ||
          name.includes('登录') ||
          name.includes('权限调试') ||
          name.includes('测试') ||
          name.includes('Test') ||
          name.includes('test')
        )) {
          result.push({
            name: name,
            path: menu.path,
            isHidden: menu.isHidden || menu.is_hidden,
            parent: parent
          });
        }
        
        if (menu.children && menu.children.length > 0) {
          result = result.concat(findTestMenus(menu.children, name));
        }
      });
      return result;
    }
    
    const testMenus = findTestMenus(data.data);
    
    console.log('\n后端菜单中的测试页面:');
    if (testMenus.length > 0) {
      console.table(testMenus);
    } else {
      console.log('  ✅ 未找到测试菜单（这是正常的）');
    }
    
    // 检查 Pinia store
    console.log('\n3️⃣ 检查 Pinia Store 中的菜单...');
    const permissionStore = window.__pinia__?.state?.value?.permission;
    if (permissionStore) {
      const storeMenus = permissionStore.menus || [];
      const storeTestMenus = findTestMenus(storeMenus);
      
      console.log('Store 中的测试菜单:');
      if (storeTestMenus.length > 0) {
        console.table(storeTestMenus);
      } else {
        console.log('  ✅ 未找到测试菜单');
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 诊断完成');
    console.log('='.repeat(60));
    
    if (testMenus.length > 0) {
      console.log('\n⚠️ 发现问题：后端返回了测试菜单');
      console.log('解决方案：需要在数据库中将这些菜单的 is_hidden 设置为 true');
    } else {
      console.log('\n✅ 后端菜单正常，测试菜单已被过滤');
      console.log('如果您仍能在菜单中看到这些项，请检查:');
      console.log('  1. 浏览器缓存是否已清理');
      console.log('  2. 页面是否已刷新');
      console.log('  3. 是否有其他地方硬编码了菜单项');
    }
  })
  .catch(err => {
    console.error('❌ 获取后端菜单失败:', err);
  });
}

