<script setup lang="ts">
import NavIcon from '@/components/NavIcon.vue'

defineEmits(['pressed'])
defineProps<{
  text: string
  colour: 'red' | 'indigo' | 'green' | 'orange' | 'blue' | 'yellow'
  icon?: string
}>()
const colourLookup = {
  red: 'var(--vt-c-red-mute)',
  indigo: 'var(--vt-c-indigo-mute)',
  green: 'var(--vt-c-green-mute)',
  orange: 'var(--vt-c-orange-mute)',
  blue: 'var(--vt-c-blue-mute)',
  yellow: 'var(--vt-c-yellow-mute)',
}
</script>

<template>
  <div class="button" @click.stop="$emit('pressed')">
    <NavIcon v-if="icon" :icon="icon" />&nbsp;{{ text }}
  </div>
</template>

<style scoped>
.button {
  background-color: v-bind(colourLookup[colour]);
  border-radius: 0.5rem;
  padding: 0.1em 0.4em;
  cursor: pointer;
  color: var(--vt-c-white);
  border: var(--color-border) solid 2px;
  font-size: 1rem;
  font-weight: bold;
  font-family:
    Verdana Bold,
    sans-serif;
  display: flex;
  align-items: center;
  justify-self: left;
  white-space: nowrap;
}
</style>
