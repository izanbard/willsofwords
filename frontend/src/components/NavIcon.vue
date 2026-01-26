<script lang="ts" setup>
defineProps<{
  icon: string
}>()
</script>

<template>
  <span class="material-symbols-outlined sized"> {{ icon }} </span>
</template>

<style scoped>
.sized {
  font-size: 1.5rem;
  font-variation-settings: 'OPSZ' 25;
  position: relative;
}
</style>
