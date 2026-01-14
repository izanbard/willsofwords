<script setup lang="ts">
import NavButton from './NavButton.vue'
</script>

<template>
  <div id="navbar" class="card">
    <NavButton text="Projects" to="/" icon="dictionary" />
    <NavButton text="Profanity" to="/profanity" icon="sentiment_stressed" />
    <NavButton text="Print Defaults" to="/print_defaults" icon="cell_merge" />
    <NavButton text="Settings" to="/settings" icon="settings" />
    <NavButton text="About" to="/about" icon="info" />
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
