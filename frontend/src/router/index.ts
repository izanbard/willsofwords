import { createRouter, createWebHistory } from 'vue-router'
import Wordsworth from '@/views/Wordsworth.vue'
import Profanity from '@/views/Profanity.vue'
import NotFound from '@/views/NotFound.vue'
import PrintDefaults from "@/views/PrintDefaults.vue";
import Settings from "@/views/Settings.vue";
import About from "@/views/About.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'projects',
      component: Wordsworth
    },
    {
      path: '/profanity',
      name: 'profanity',
      component: Profanity
    },
    {
      path: '/print_defaults',
      name: 'print_defaults',
      component: PrintDefaults
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    },
    {
      path: '/about',
      name: 'about',
      component: About
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound
    }
  ],
})

export default router
