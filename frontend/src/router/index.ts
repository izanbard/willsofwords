import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '@/views/ProjectsView.vue'
import ProfanityView from '@/views/ProfanityView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import PrintDefaultsView from "@/views/PrintDefaultsView.vue";
import SettingsView from "@/views/SettingsView.vue";
import AboutView from "@/views/AboutView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'projects',
      component: ProjectsView
    },
    {
      path: '/profanity',
      name: 'profanity',
      component: ProfanityView
    },
    {
      path: '/print_defaults',
      name: 'print_defaults',
      component: PrintDefaultsView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFoundView',
      component: NotFoundView
    }
  ],
})

export default router
