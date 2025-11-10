/**
 * 数据模型管理路由配置
 * 
 * 说明：此文件定义"数据模型管理"菜单及其子路由
 * 该路由将被动态加载到主路由系统中
 */

const Layout = () => import('@/layout/index.vue')

export default {
  name: 'DataModel',
  path: '/data-model',
  component: Layout,
  redirect: '/data-model/config',
  meta: {
    title: '数据模型管理',
    icon: 'database',
    order: 50, // 排序：在中间位置
    requiresAuth: true,
  },
  children: [
    {
      name: 'DataModelFields',
      path: 'fields',
      component: () => import('./fields/index.vue'),
      meta: {
        title: '字段定义管理',
        icon: 'list',
        requiresAuth: true,
      },
    },
    {
      name: 'DataModelConfig',
      path: 'config',
      component: () => import('./config/index.vue'),
      meta: {
        title: '模型配置管理',
        icon: 'settings',
        requiresAuth: true,
      },
    },
    {
      name: 'DataModelMapping',
      path: 'mapping',
      component: () => import('./mapping/index.vue'),
      meta: {
        title: '字段映射管理',
        icon: 'link',
        requiresAuth: true,
      },
    },
    {
      name: 'DataModelPreview',
      path: 'preview',
      component: () => import('./preview/index.vue'),
      meta: {
        title: '预览与测试',
        icon: 'eye',
        requiresAuth: true,
      },
    },
  ],
}

