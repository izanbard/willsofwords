import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '@/views/ProjectsView.vue'
import ProfanityView from '@/views/ProfanityView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import ProjectDefaultsView from '@/views/ProjectDefaultsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import AboutView from '@/views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'projects',
      component: ProjectsView,
    },
    {
      path: '/profanity',
      name: 'profanity',
      component: ProfanityView,
    },
    {
      path: '/project_defaults',
      name: 'project_defaults',
      component: ProjectDefaultsView,
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFoundView',
      component: NotFoundView,
    },
  ],
})

export default router
