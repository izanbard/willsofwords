<script setup lang="ts">
import {computed} from "vue";

const props = defineProps<{ thickness?: number }>()
const size = computed(() => {
  return props.thickness ? `${props.thickness}px` : '1px'
})
</script>

<template>
<hr/>
</template>

<style scoped>
hr {
  border: 0;
  border-top: v-bind('size') solid var(--vt-c-divider-light-1);
  margin: 1rem 0;
}
</style>
