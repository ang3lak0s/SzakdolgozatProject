import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

if (import.meta.env.DEV) {
  localStorage.removeItem('user-token')
}

createApp(App).use(router).mount('#app')
