<script setup lang="ts">
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { onBeforeMount, ref } from 'vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import axios from 'axios'
import { useToast } from 'vue-toast-notification'
import DividerLine from '@/components/DividerLine.vue'
import PuzzleBlock from '@/components/PuzzleBlock.vue'
import InputBlock from '@/components/InputBlock.vue'

interface PuzzleBaseData {
  title: string
  puzzle_list: string[]
  page_count: number
}

const loading = ref(true)
const toast = useToast()
const { project_name } = defineProps<{ project_name: string }>()
const puzzle_base_data = ref<PuzzleBaseData>({
  title: '',
  puzzle_list: [],
  page_count: 0,
} as PuzzleBaseData)

onBeforeMount(async () => {
  await load_base_data()
})
const load_base_data = async () => {
  await axios
    .get(`/projects/project/${project_name}/puzzledata/base_data/`)
    .then((response) => {
      puzzle_base_data.value = response.data
    })
    .catch((error) => {
      toast.error('Error fetching puzzle base data:', error.message)
    })
  loading.value = false
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <HeadingBlock :level="1">Puzzle View</HeadingBlock>
    <HeadingBlock :level="2">Book Title: {{ puzzle_base_data.title }}</HeadingBlock>
    <InputBlock
      type="int"
      v-model="puzzle_base_data.page_count"
      description="Number of pages in book"
      readonly
      unit="pages"
      >Page Count:</InputBlock
    >
    <DividerLine :thickness="5" />
    <template v-for="(puzzle_id, index) in puzzle_base_data.puzzle_list" :key="index">
      <PuzzleBlock :project_name="project_name" :puzzle_id="puzzle_id" />
    </template>
  </div>
</template>

<style scoped></style>
