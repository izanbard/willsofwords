<script setup lang="ts">
import axios from 'axios'
const emit = defineEmits(['reload', 'modal'])
defineProps<{ word: string }>()
const remove_word = async (word: string) => {
  emit('modal')
  await axios.delete('/settings/profanity/', { params: { word: word } })
  emit('reload')
}
</script>

<template>
  <div class="tile">
    <div>{{ word }}</div>
    <span class="material-symbols-outlined sized" @click="remove_word(word)">delete</span>
  </div>
</template>

<style scoped>
.tile {
  background-color: var(--color-background-wow);
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
