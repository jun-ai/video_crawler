import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/materials',
    name: 'Materials',
    component: () => import('@/views/Materials.vue')
  },
  {
    path: '/learn/:id',
    name: 'Learn',
    component: () => import('@/views/Learn.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/Favorites.vue')
  },
  {
    path: '/vocabulary',
    name: 'Vocabulary',
    component: () => import('@/views/Vocabulary.vue')
  },
  {
    path: '/vocabulary-review',
    name: 'VocabularyReview',
    component: () => import('@/views/VocabularyReview.vue')
  },
  {
    path: '/english-cards',
    name: 'EnglishCards',
    component: () => import('@/views/EnglishCards.vue')
  },
  {
    path: '/learning-center',
    name: 'LearningCenter',
    component: () => import('@/views/LearningCenter.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { noindex: true }  // P1-11: 认证页不让搜索引擎抓
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { noindex: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { noindex: true }
  },
  // P0 商业化合规: 用户协议 / 隐私政策 / 退换政策
  // (合规页应该被 index, 客户能看到, 加 canonical 让 SEO 收录)
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/views/Terms.vue'),
    meta: { title: '用户协议 - Fluenty' }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/views/Privacy.vue'),
    meta: { title: '隐私政策 - Fluenty' }
  },
  {
    path: '/refund',
    name: 'Refund',
    component: () => import('@/views/Refund.vue'),
    meta: { title: '退换政策 - Fluenty' }
  },
  // P3 组件展示页(开发环境,生产可保留)
  {
    path: '/_showcase',
    name: 'Showcase',
    component: () => import('@/views/Showcase.vue')
  },
  // 管理员路由
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue')
      },
      {
        path: 'materials',
        name: 'AdminMaterials',
        component: () => import('@/views/admin/MaterialsManage.vue')
      },
      {
        path: 'upload',
        component: () => import('@/views/admin/UploadLayout.vue'),
        children: [
          {
            path: '',
            name: 'AdminUpload',
            component: () => import('@/views/admin/MaterialUpload.vue')
          },
          {
            path: 'fetch-url',
            name: 'AdminUploadFetchUrl',
            component: () => import('@/views/admin/upload/FetchFromUrl.vue')
          },
          {
            path: 'transcribe',
            name: 'AdminUploadTranscribe',
            component: () => import('@/views/admin/upload/Transcribe.vue')
          }
        ]
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import('@/views/admin/TagsManage.vue')
      },
      {
        path: 'activation-codes',
        name: 'AdminActivationCodes',
        component: () => import('@/views/admin/ActivationCodesManage.vue')
      },
      {
        path: 'announcements',
        name: 'AdminAnnouncements',
        component: () => import('@/views/admin/AnnouncementsManage.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 需要管理员权限的路由
  if (to.meta.requiresAdmin) {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    if (!userStore.isAdmin) {
      next({ name: 'Home' })
      return
    }
  }

  next()
})

// P1-11: 动态设置 <meta name="robots"> 和 <title>
// 认证页 (login/register/forgot-password) 加 noindex, 防止搜索引擎抓
// 合规页 + 普通页保持 indexable
router.afterEach((to) => {
  // 1. robots meta
  let robotsMeta = document.querySelector('meta[name="robots"]')
  if (!robotsMeta) {
    robotsMeta = document.createElement('meta')
    robotsMeta.setAttribute('name', 'robots')
    document.head.appendChild(robotsMeta)
  }
  robotsMeta.setAttribute('content', to.meta.noindex ? 'noindex,nofollow' : 'index,follow')

  // 2. title (优先用 route meta.title, 否则用默认)
  if (to.meta.title) {
    document.title = to.meta.title
  } else {
    document.title = 'Fluenty — 英语口语学习'
  }
})

export default router
