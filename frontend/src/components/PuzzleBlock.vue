<script setup lang="ts">
import { useToast } from 'vue-toast-notification'
import { onBeforeMount, onMounted, ref } from 'vue'
import axios from 'axios'
import DividerLine from '@/components/DividerLine.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import InputBlock from '@/components/InputBlock.vue'
import WordTile from '@/components/WordTile.vue'

interface Cell {
  loc_x: number
  loc_y: number
  value: string
  is_answer: boolean
  direction: { NS: boolean; EW: boolean; NESW: boolean; NWSE: boolean }
}

interface PuzzleData {
  project_config: Record<string, string | number | boolean>
  puzzle_id: string
  puzzle_title: string
  display_title: string
  input_word_list: string[]
  long_fact: string
  short_fact: string
  rows: number
  columns: number
  cells: Cell[][]
  puzzle_search_list: string[]
  density: number
  profanity: Record<string, (string | (string | number)[])[]>
}

const { project_name, puzzle_id } = defineProps<{ project_name: string; puzzle_id: string }>()
const toast = useToast()
const loading = ref(true)
const puzzle_data = ref<PuzzleData>({
  project_config: {},
  puzzle_id: '',
  puzzle_title: '',
  display_title: '',
  input_word_list: [],
  long_fact: '',
  short_fact: '',
  rows: 0,
  columns: 0,
  cells: [[]],
  puzzle_search_list: [],
  density: 0,
  profanity: {},
})
const load_puzzle_data = async () => {
  await axios
    .get(`/projects/project/${project_name}/puzzledata/puzzle/${puzzle_id}/`)
    .then((response) => {
      puzzle_data.value = response.data
    })
    .catch((error) => {
      toast.error('Error fetching puzzle data:', error.message)
    })
  loading.value = false
}

onMounted(async () => {
  await load_puzzle_data()
})
</script>

<template>
  <HeadingBlock :level="2">{{ puzzle_data.display_title }}</HeadingBlock>
  <div class="puzzle_data">
    <InputBlock type="text" v-model="puzzle_data.puzzle_id" readonly>Puzzle ID:</InputBlock>
    <InputBlock type="text" v-model="puzzle_data.puzzle_title">Puzzle Title:</InputBlock>
    <InputBlock type="text" v-model="puzzle_data.display_title">Display Title:</InputBlock>
    <InputBlock type="textarea" v-model="puzzle_data.long_fact">Long Fact:</InputBlock>
    <InputBlock type="textarea" v-model="puzzle_data.short_fact">Short Fact:</InputBlock>
    <InputBlock type="text" v-model="puzzle_data.density" readonly>Density:</InputBlock>
    <InputBlock type="text" v-model="puzzle_data.rows" readonly>Rows:</InputBlock>
    <InputBlock type="text" v-model="puzzle_data.columns" readonly>Columns:</InputBlock>
    <div class="search_words">
      <div class="label">Input Words:</div>
      <div class="words">
        <template v-for="(word, index) in puzzle_data.input_word_list" :key="index">
          <InputBlock
            type="text"
            v-model="puzzle_data.input_word_list[index]"
            withButton
            buttonIcon="delete"
            buttonColor="red"
            @pressed="puzzle_data.input_word_list.splice(index, 1)"
          />
        </template>
      </div>
    </div>
    <div class="search_words">
      <div class="label">Search Words:</div>
      <div class="words">
        <template v-for="(word, index) in puzzle_data.puzzle_search_list" :key="index">
          <WordTile :word="word" :delete_button="false" />
        </template>
      </div>
    </div>
  </div>
  <div class="puzzle_grids">
    <div class="puzzle_grid">
      <template v-if="puzzle_data.cells" v-for="(row, y) in puzzle_data.cells" :key="y">
        <template v-if="puzzle_data.cells[y]" v-for="(cell, x) in row" :key="x">
          <LetterTile v-model="puzzle_data.cells[y][x]" :solution="false">{{
            cell.value
          }}</LetterTile>
        </template>
      </template>
    </div>
    <div class="puzzle_grid">
      <template v-if="puzzle_data.cells" v-for="(row, y) in puzzle_data.cells" :key="y">
        <template v-if="puzzle_data.cells[y]" v-for="(cell, x) in row" :key="x">
          <LetterTile v-model="puzzle_data.cells[y][x]" :solution="true">{{
            cell.value
          }}</LetterTile>
        </template>
      </template>
    </div>
  </div>
  <DividerLine />
</template>

<style scoped>
.puzzle_data {
  display: flex;
  flex-direction: column;
}
.search_words {
  display: flex;
}
.label {
  white-space: nowrap;
  padding: 0.5rem;
}
.words {
  display: flex;
  flex-wrap: wrap;
}
.puzzle_grids {
  display: flex;
  justify-content: space-evenly;
}
.puzzle_grid {
  display: grid;
  --puzzle-rows: v-bind(puzzle_data.rows);
  --puzzle-columns: v-bind(puzzle_data.columns);
  grid-template-columns: repeat(var(--puzzle-columns), 20px);
  grid-template-rows: repeat(var(--puzzle-rows), 20px);
}
</style>
