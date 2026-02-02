import './assets/main.css'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import axios from 'axios'
import ToastPlugin from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-default.css'

const app = createApp(App)

axios.defaults.baseURL = 'http://' + import.meta.env.VITE_API_BASE_URL
app.use(ToastPlugin, {
  position: 'bottom-right',
})
app.use(router)

app.mount('#app')
