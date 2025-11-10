/**
 * 权限状态管理 Store
 * 迁移到 TypeScript + Shared 层类型定义
 */
import { defineStore } from 'pinia'
import type { Menu } from '@device-monitor/shared/types'
import { basicRoutes, vueModules } from '@/router/routes'
import api from '@/api'
import { apiV2 } from '@/api/v2'
import { authApi } from '@/api/system-v2'
import { useUserStore } from '@/store/modules/user'
import type { RouteRecordRaw } from 'vue-router'

// 使用动态导入Layout组件
const Layout = () => import('@/layout/index.vue')

/**
 * 后端菜单数据接口（与后端返回格式对应）
 */
interface BackendMenu {
  name: string
  path: string
  icon?: string
  order?: number
  is_hidden?: boolean
  keepalive?: boolean
  redirect?: string
  component?: string
  children?: BackendMenu[]
}

/**
 * Permission Store 状态接口
 */
interface PermissionState {
  accessRoutes: RouteRecordRaw[]
  accessApis: string[]
  isLoadingApis: boolean
}

/**
 * 查找组件函数
 */
function findComponent(path: string | undefined | null) {
  if (!path || typeof path !== 'string') {
    console.warn(`Invalid component path: ${path}`)
    return null
  }

  // 移除开头的 '/' 并清理路径
  let cleanPath = path.startsWith('/') ? path.substring(1) : path

  // 移除多余的斜杠并清理空段
  cleanPath = cleanPath
    .split('/')
    .filter((segment) => segment.trim() !== '')
    .join('/')

  if (!cleanPath) {
    console.warn(`Empty component path after cleaning: ${path}`)
    return null
  }

  // 构造两种可能的路径
  const path1 = `/src/views/${cleanPath}/index.vue`
  const path2 = `/src/views/${cleanPath}.vue`

  // 检查哪个路径存在于 vueModules 中
  if (vueModules[path1]) {
    return vueModules[path1]
  }
  if (vueModules[path2]) {
    return vueModules[path2]
  }

  // 如果都找不到，打印警告并返回 null
  console.warn(
    `Component not found for path: ${path}. Cleaned path: ${cleanPath}. Tried: ${path1} and ${path2}`
  )
  return null
}

/**
 * 根据后端传来数据构建出前端路由
 */
function buildRoutes(routes: BackendMenu[] = []): RouteRecordRaw[] {
  return routes.map((e) => {
    // 父路由路径：确保以 '/' 开头
    const normalizedPath = e.path && !e.path.startsWith('/') ? `/${e.path}` : e.path
    
    const route: RouteRecordRaw = {
      name: e.name,
      path: normalizedPath,
      component: Layout,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
        isHidden: e.is_hidden,
      },
      redirect: e.redirect,
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => {
        const component = findComponent(e_child.component)
        // 子路由路径：应该是相对路径，移除前导斜杠
        let childPath = e_child.path
        if (childPath && childPath.startsWith('/')) {
          childPath = childPath.substring(1)
        }
        
        const routeInfo: RouteRecordRaw = {
          name: e_child.name,
          path: childPath,
          component: component || (() => import('@/views/error-page/404.vue')),
          meta: {
            title: e_child.name,
            icon: e_child.icon,
            order: e_child.order,
            keepAlive: e_child.keepalive,
            isHidden: e_child.is_hidden,
          },
        }

        // 强制为菜单管理页面开启 keepAlive 并同步 name
        if (e_child.name === '菜单管理') {
          routeInfo.name = 'SystemMenu'
          if (routeInfo.meta) {
            routeInfo.meta.keepAlive = true
          }
        }

        return routeInfo
      })
    } else {
      // 没有子菜单，创建一个默认的子路由
      const component = e.component === 'Layout' ? null : findComponent(e.component)
      route.children = [{
        name: `${e.name}Default`,
        path: '',
        component: component || (() => import('@/views/error-page/404.vue')),
        meta: {
          title: e.name,
          icon: e.icon,
          order: e.order,
          keepAlive: e.keepalive,
          isHidden: true,
        },
      }]
    }

    return route
  })
}

// 导出增强版权限Store
export { useEnhancedPermissionStore, PermissionType, PermissionMode } from './enhanced-permission-store'

/**
 * 权限 Store
 */
export const usePermissionStore = defineStore('permission', {
  state: (): PermissionState => ({
    accessRoutes: [],
    accessApis: [],
    isLoadingApis: false,
  }),

  getters: {
    /**
     * 所有路由（基础路由 + 权限路由）
     */
    routes(): RouteRecordRaw[] {
      return basicRoutes.concat(this.accessRoutes)
    },

    /**
     * 菜单列表（过滤隐藏菜单）
     */
    menus(): RouteRecordRaw[] {
      return this.routes.filter((route) => route.name && !route.meta?.isHidden)
    },

    /**
     * API 权限列表
     */
    apis(): string[] {
      return this.accessApis
    },
  },

  actions: {
    /**
     * 生成路由
     */
    async generateRoutes(): Promise<RouteRecordRaw[]> {
      console.log('✅ Shared API: permissionStore.generateRoutes() - 使用 Shared Menu 类型')
      console.log('permissionStore.generateRoutes: Calling apiV2.getUserMenu()')
      
      const res = await apiV2.getUserMenu() // 调用v2版本接口获取后端传来的菜单路由
      console.log('permissionStore.generateRoutes: Received response from apiV2.getUserMenu()', res)
      
      this.accessRoutes = buildRoutes(res.data) // 处理成前端路由格式
      return this.accessRoutes
    },

    /**
     * 获取用户 API 权限
     */
    async getAccessApis(): Promise<string[] | undefined> {
      try {
        // 首先检查是否正在登出，如果是则立即返回
        const userStore = useUserStore()
        if (userStore.isLoggingOut) {
          console.log('permissionStore.getAccessApis: 正在登出中，跳过权限API调用')
          return
        }
        
        // 检查token是否存在，如果不存在则不调用API
        if (!userStore.token) {
          console.log('permissionStore.getAccessApis: 无token，跳过权限API调用')
          return
        }
        
        this.isLoadingApis = true
        console.log('✅ Shared API: permissionStore.getAccessApis()')
        console.log('permissionStore.getAccessApis: Calling authApi.getUserApis()')
        
        // 在API调用前再次检查登出状态
        if (userStore.isLoggingOut) {
          console.log('permissionStore.getAccessApis: API调用前检测到登出状态，取消调用')
          return
        }
        
        const res = await authApi.getUserApis()
        
        // API调用完成后再次检查登出状态
        if (userStore.isLoggingOut) {
          console.log('permissionStore.getAccessApis: API调用完成后检测到登出状态，忽略结果')
          return
        }
        
        console.log('permissionStore.getAccessApis: Received response from authApi.getUserApis()', res)
        this.accessApis = res.data
        return this.accessApis
      } catch (error: any) {
        console.error('permissionStore.getAccessApis: Error loading APIs', error)
        
        // 检查是否是登出过程中的错误，如果是则不抛出异常
        const userStore = useUserStore()
        if (userStore.isLoggingOut) {
          console.log('permissionStore.getAccessApis: 登出过程中的API错误，忽略')
          return
        }
        
        // 如果是401错误且不在登出状态，记录但不抛出异常避免弹窗
        if (error.response?.status === 401) {
          console.log('permissionStore.getAccessApis: 401错误，可能需要重新登录')
          return
        }
        
        throw error
      } finally {
        this.isLoadingApis = false
      }
    },

    /**
     * 重置权限数据
     */
    resetPermission(): void {
      this.$reset()
    },
  },
})

