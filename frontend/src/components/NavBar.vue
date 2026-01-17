<script setup lang="ts">
import NavButton from './NavButton.vue'
</script>

<template>
  <div id="navbar" class="card">
    <NavButton text="Projects" :to="{ name: 'projects' }" icon="dictionary" />
    <NavButton text="Profanity" :to="{ name: 'profanity' }" icon="sentiment_stressed" />
    <NavButton text="Project Defaults" :to="{ name: 'project_defaults' }" icon="cell_merge" />
    <NavButton text="Settings" :to="{ name: 'settings' }" icon="settings" />
    <NavButton text="About" :to="{ name: 'about' }" icon="info" />
  </div>
</template>

<style scoped>
#navbar {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-evenly;
  align-items: center;
}
</style>
