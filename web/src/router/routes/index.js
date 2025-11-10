import i18n from '~/i18n'
const { t } = i18n.global

const Layout = () => import('@/layout/index.vue')

export const basicRoutes = [
  {
    path: '/',
    redirect: '/workbench', // 默认跳转到首页
    meta: { order: 0 },
  },
  {
    name: t('views.workbench.label_workbench'),
    path: '/workbench',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/workbench/index.vue'),
        name: `${t('views.workbench.label_workbench')}Default`,
        meta: {
          title: t('views.workbench.label_workbench'),
          icon: 'icon-park-outline:workbench',
          affix: true,
        },
      },
    ],
    meta: { order: 1 },
  },
  {
    name: t('views.profile.label_profile'),
    path: '/profile',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/profile/index.vue'),
        name: `${t('views.profile.label_profile')}Default`,
        meta: {
          title: t('views.profile.label_profile'),
          icon: 'user',
          affix: true,
        },
      },
    ],
    meta: { 
      order: 99,
      isHidden: true,
    },
  },
  // {
  //   name: 'ErrorPage',
  //   path: '/error-page',
  //   component: Layout,
  //   redirect: '/error-page/404',
  //   meta: {
  //     title: t('views.errors.label_error'),
  //     icon: 'mdi:alert-circle-outline',
  //     order: 99,
  //   },
  //   children: [
  //     {
  //       name: 'ERROR-401',
  //       path: '401',
  //       component: () => import('@/views/error-page/401.vue'),
  //       meta: {
  //         title: '401',
  //         icon: 'material-symbols:authenticator',
  //       },
  //     },
  //     {
  //       name: 'ERROR-403',
  //       path: '403',
  //       component: () => import('@/views/error-page/403.vue'),
  //       meta: {
  //         title: '403',
  //         icon: 'solar:forbidden-circle-line-duotone',
  //       },
  //     },
  //     {
  //       name: 'ERROR-404',
  //       path: '404',
  //       component: () => import('@/views/error-page/404.vue'),
  //       meta: {
  //         title: '404',
  //         icon: 'tabler:error-404',
  //       },
  //     },
  //     {
  //       name: 'ERROR-500',
  //       path: '500',
  //       component: () => import('@/views/error-page/500.vue'),
  //       meta: {
  //         title: '500',
  //         icon: 'clarity:rack-server-outline-alerted',
  //       },
  //     },
  //   ],
  // },
  {
    name: '403',
    path: '/403',
    component: () => import('@/views/error-page/403.vue'),
    meta: {
      isHidden: true,
    },
  },
  {
    name: '404',
    path: '/404',
    component: () => import('@/views/error-page/404.vue'),
    meta: {
      isHidden: true,
    },
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录页',
      isHidden: true,
    },
  },
  // 测试路由已注释 - 生产环境不需要显示
  // {
  //   name: 'PermissionDebug',
  //   path: '/permission-debug',
  //   component: () => import('@/views/permission-debug.vue'),
  //   isHidden: true,
  //   meta: {
  //     title: '权限调试',
  //   },
  // },
  // {
  //   name: 'SimpleTest',
  //   path: '/simple-test',
  //   component: () => import('@/views/simple-test.vue'),
  //   isHidden: true,
  //   meta: {
  //     title: '简单测试',
  //   },
  // },
  // {
  //   name: 'TestPermission',
  //   path: '/test-permission',
  //   component: () => import('@/views/test/permission-test.vue'),
  //   isHidden: true,
  //   meta: {
  //     title: '权限测试',
  //   },
  // },
  // {
  //   name: 'TestComponents',
  //   path: '/test-components',
  //   component: () => import('@/views/test/permission-components.vue'),
  //   isHidden: true,
  //   meta: {
  //     title: '权限组件测试',
  //   },
  // },
]

export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  redirect: '/404',
  isHidden: true,
}

export const EMPTY_ROUTE = {
  name: 'Empty',
  path: '/:pathMatch(.*)*',
  component: null,
}

const modules = import.meta.glob('@/views/**/route.{js,ts}', { eager: true })
const asyncRoutes = []
Object.keys(modules).forEach((key) => {
  asyncRoutes.push(modules[key].default)
})

// 加载 views 下每个模块的 index.vue 文件
const vueModules = import.meta.glob('@/views/**/index.vue')

export { asyncRoutes, vueModules }
