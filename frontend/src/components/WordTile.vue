<script setup lang="ts">
defineEmits(['delete'])
const {
  word,
  delete_button = true,
  colour = 'var(--color-background-wow)',
} = defineProps<{ word: string; delete_button: boolean; colour?: string }>()
</script>

<template>
  <div class="tile">
    <div>{{ word }}</div>
    <span
      v-if="delete_button"
      class="material-symbols-outlined sized"
      @click="$emit('delete', word)"
      >delete</span
    >
  </div>
</template>

<style scoped>
.tile {
  --my_colour: v-bind(colour);
  background-color: var(--my_colour);
  border-radius: 0.5rem;

  border: var(--color-border) solid 2px;
  padding: 0.1rem 0.4rem;

  display: grid;
  grid-template-columns: auto 1rem;
  align-items: center;
  margin: 0.1rem;
}

.sized {
  font-size: 1.2rem;
  color: var(--vt-c-red-mute);
  font-variation-settings: 'OPSZ' 25;
  cursor: pointer;
}
</style>
