import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '@/views/ProjectsView.vue'
import ProfanityView from '@/views/ProfanityView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import ProjectDefaultsView from '@/views/ProjectDefaultsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import AboutView from '@/views/AboutView.vue'
import ProjectView from '@/views/ProjectView.vue'

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
      props: { create: false },
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
      path: '/projects/new',
      name: 'create-project',
      component: ProjectDefaultsView,
      props: { create: true },
    },
    {
      path: '/project/:project_name',
      name: 'project',
      component: ProjectView,
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFoundView',
      component: NotFoundView,
    },
  ],
})

export default router
