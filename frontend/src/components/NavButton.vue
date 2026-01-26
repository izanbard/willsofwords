<script setup lang="ts">
import NavIcon from '@/components/NavIcon.vue'

defineProps<{
  icon: string
  text: string
  to: string | object
}>()
</script>

<template>
  <RouterLink :to="to" class="nav_link">
    <div class="nav_button">
      <NavIcon :icon="icon" size="small" />
      <span class="title">{{ text }}</span>
    </div>
  </RouterLink>
</template>

<style scoped>
.nav_link {
  text-decoration: none;
  color: var(--color-heading);
}

.nav_button {
  background-color: var(--color-background-wow);
  border-radius: 0.5rem;

  border: var(--color-border) solid 2px;
  padding: 0.1em 0.4em;
  line-height: 0;
  display: flex;
  align-items: center;
}

.title {
  font-size: 1rem;
  font-weight: bold;
  font-family:
    Verdana Bold,
    sans-serif;
}
</style>
