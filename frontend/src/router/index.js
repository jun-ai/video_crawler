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
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue')
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
        name: 'AdminUpload',
        component: () => import('@/views/admin/MaterialUpload.vue')
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

export default router
