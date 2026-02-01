import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '@/views/ProjectsView.vue'
import ProfanityView from '@/views/ProfanityView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import ProjectSettingsView from '@/views/ProjectSettingsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import AboutView from '@/views/AboutView.vue'
import ProjectView from '@/views/ProjectView.vue'
import WordlistView from '@/views/WordlistView.vue'
import PuzzleView from '@/views/PuzzleView.vue'
import CreateWordlistView from '@/views/CreateWordlistView.vue'

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
      component: ProjectSettingsView,
      props: { mode: 'defaults' },
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
      component: ProjectSettingsView,
      props: { mode: 'new' },
    },
    {
      path: '/project/:project_name',
      name: 'project',
      component: ProjectView,
      props: true,
      children: [
        {
          path: 'settings/:mode',
          name: 'edit-project-settings',
          component: ProjectSettingsView,
          props: (route) => ({ project_name: route.params.project_name, mode: route.params.mode }),
        },
        {
          path: 'wordlist/edit',
          name: 'edit-wordlist',
          component: WordlistView,
          props: true,
        },
        {
          path: 'wordlist/create',
          name: 'create-wordlist',
          component: CreateWordlistView,
          props: true,
        },
        {
          path: 'puzzledata',
          name: 'edit-puzzledata',
          component: PuzzleView,
          props: true,
        },
      ],
    },
    {
      path: '/experimental',
      component: CreateWordlistView,
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
