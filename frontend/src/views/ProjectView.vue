<script setup lang="ts">
const { project_name } = defineProps<{ project_name: string }>()
import HeadingBlock from '@/components/HeadingBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
</script>

<template>
  <div class="card">
    <HeadingBlock :level="1">{{ project_name }}</HeadingBlock>
    <DividerLine />
  </div>
</template>

<style scoped></style>
