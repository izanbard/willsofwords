<script lang="ts" setup>
import { computed, type ComputedRef } from 'vue'

const props = defineProps<{
  icon: string
  size: string
}>()
const size_lookup: Record<string, number> = {
  large: 40,
  medium: 25,
  small: 1.5,
}
const icon_size: ComputedRef<number|undefined> = computed(() => {
  return props.size && props.size in size_lookup ? size_lookup[props.size] : 20
})
</script>

<template>
  <span class="material-symbols-outlined sized"> {{ icon }} </span>
</template>

<style scoped>
.sized {
  font-size: v-bind(icon_size + 'rem');
  font-variation-settings: 'OPSZ' v-bind(icon_size);
  position: relative;
}
</style>
