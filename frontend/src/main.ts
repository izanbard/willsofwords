import './assets/main.css'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL

app.use(router)

app.mount('#app')
