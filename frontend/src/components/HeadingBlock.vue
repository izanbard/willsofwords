<script setup lang="ts">
defineProps<{
  level: number
}>()
</script>

<template>
  <div :class="'h'+level">
    <slot></slot>
  </div>
</template>

<style scoped>
.h1,
.h2 {
  margin: 0.5rem 0;
  color: var(--color-heading);
  font-weight: bold;
  font-family: 'Verdana Bold', sans-serif;
}

.h1 {
  font-size: 1.6rem;
}

.h2 {
  font-size: 1.2rem;
}
</style>
