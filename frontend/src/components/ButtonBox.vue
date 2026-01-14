<script setup lang="ts">
defineEmits(['pressed'])
defineProps<{
  text: string,
  colour: 'red' | 'indigo' | 'green' | 'orange' | 'blue'|'yellow'
}>()
const colourLookup = {
  red: 'var(--vt-c-red-mute)',
  indigo: 'var(--vt-c-indigo-mute)',
  green: 'var(--vt-c-green-mute)',
  orange: 'var(--vt-c-orange-mute)',
  blue: 'var(--vt-c-blue-mute)',
  yellow: 'var(--vt-c-yellow-mute)'
}
</script>

<template>
<span class="button" @click="$emit('pressed')">{{ text }}</span>
</template>

<style scoped>
.button {
  background-color: v-bind(colourLookup[colour]);
  border-radius: 0.5rem;
  padding: 0.2rem;
  cursor: pointer;
  color: var(--vt-c-white);
  border: var(--color-border) solid 2px;
  font-size: 1rem;
}
</style>
