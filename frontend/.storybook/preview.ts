import type { Preview } from '@storybook/vue3'
import { setup } from '@storybook/vue3'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { withThemeByClassName } from '@storybook/addon-themes'
import '../src/styles/tailwind.css'

// Pinia 单例
setActivePinia(createPinia())

// Router 单例 (默认路由, 避免 stories 路由报错)
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } }
  ]
})

setup((app) => {
  app.use(createPinia())
  app.use(router)
})

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/
      }
    },
    layout: 'centered',
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a2e' }
      ]
    }
  },
  decorators: [
    withThemeByClassName({
      themes: {
        light: 'light',
        dark: 'dark'
      },
      defaultTheme: 'light'
    })
  ]
}

export default preview
