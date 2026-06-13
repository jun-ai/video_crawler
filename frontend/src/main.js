import { createApp } from 'vue'
import { createPinia } from 'pinia'

import './styles/tailwind.css'
import './styles/design-tokens.css'
import './styles/global.css'
import './styles/responsive.css'

import App from './App.vue'
import router from './router'
import vLoading from './directives/v-loading'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.directive('loading', vLoading)

app.mount('#app')
