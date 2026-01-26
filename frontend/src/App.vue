<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import TitleBar from '@/components/TitleBar.vue'
import NavBar from '@/components/NavBar.vue'

const icon_list: string[] = [
  'add',
  'cancel',
  'cell_merge',
  'change_circle',
  'check_circle',
  'create_new_folder',
  'delete',
  'dictionary',
  'edit',
  'error',
  'folder_copy',
  'info',
  'save',
  'sentiment_stressed',
  'settings',
  'warning',
]

const title: string = 'Wordsworth - Wills of Words'

onMounted(() => {
  const google_icons_link: HTMLLinkElement = document.createElement('link')
  google_icons_link.setAttribute('rel', 'stylesheet')
  const href: string =
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&icon_names=' +
    icon_list.sort().join(',') +
    '&display=block'
  google_icons_link.setAttribute('href', href)
  document.head.appendChild(google_icons_link)
  document.head.title = title
})
</script>

<template>
  <header>
    <TitleBar />
    <NavBar />
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style scoped></style>
