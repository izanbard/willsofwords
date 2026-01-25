<script setup lang="ts">
import { useToast } from 'vue-toast-notification'
import { onMounted, ref } from 'vue'
import axios from 'axios'
import DividerLine from '@/components/DividerLine.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import InputBlock from '@/components/InputBlock.vue'
import WordTile from '@/components/WordTile.vue'
import ButtonBox from '@/components/ButtonBox.vue'
import PuzzleGrid from '@/components/PuzzleGrid.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import GridTile from '@/components/GridTile.vue'

interface Cell {
  loc_x: number
  loc_y: number
  value: string
  is_answer: boolean
  is_profane: boolean
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
  profanity: Record<string, (string | (string | number)[])[][]>
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
  cells: [[]] as Cell[][],
  puzzle_search_list: [],
  density: 0,
  profanity: {},
})

const load_puzzle_data = async () => {
  loading.value = true
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
const save_puzzle = async () => {
  loading.value = true
  await axios
    .put(`/projects/project/${project_name}/puzzledata/puzzle/${puzzle_id}/`, puzzle_data.value)
    .then(async () => {
      toast.success('Puzzle saved successfully')
      await load_puzzle_data()
    })
    .catch((error) => {
      toast.error('Error saving puzzle:', error.message)
    })
}
const rebuild_puzzle = async () => {
  loading.value = true
  await axios
    .delete(`/projects/project/${project_name}/puzzledata/puzzle/${puzzle_id}/`)
    .then(async () => {
      toast.success('Puzzle rebuilt successfully')
      await load_puzzle_data()
    })
    .catch((error) => {
      toast.error('Error rebuilding puzzle:', error.message)
    })
}
</script>

<template>
  <div class="puzzle_block_container">
    <LoadingSpinner :loading="loading" :local="true" />
    <HeadingBlock :level="2">{{ puzzle_data.display_title }}</HeadingBlock>
    <div class="actions">
      <ButtonBox icon="save" text="Save Changes" colour="green" @pressed="save_puzzle" />
      <ButtonBox
        icon="change_circle"
        text="Rebild Puzzle"
        colour="blue"
        @pressed="rebuild_puzzle"
      />
      <ButtonBox icon="cancel" text="Revert to Saved" colour="indigo" @pressed="load_puzzle_data" />
    </div>
    <div class="puzzle_data">
      <InputBlock type="text" v-model="puzzle_data.puzzle_id" readonly>Puzzle ID:</InputBlock>
      <InputBlock type="text" v-model="puzzle_data.puzzle_title">Puzzle Title:</InputBlock>
      <InputBlock type="text" v-model="puzzle_data.display_title">Display Title:</InputBlock>
      <InputBlock type="textarea" v-model="puzzle_data.long_fact">Long Fact:</InputBlock>
      <InputBlock type="textarea" v-model="puzzle_data.short_fact">Short Fact:</InputBlock>
      <InputBlock type="text" v-model="puzzle_data.density" readonly>Density:</InputBlock>
      <InputBlock type="text" v-model="puzzle_data.rows" readonly>Rows:</InputBlock>
      <InputBlock type="text" v-model="puzzle_data.columns" readonly>Columns:</InputBlock>
      <DividerLine />
      <CalloutBox type="info"
        >Words highlighted in red are in the input, but not used in the actual puzzle</CalloutBox
      >
      <div class="search_words">
        <div class="label">Input Words:</div>
        <div class="words">
          <template v-for="(word, index) in puzzle_data.input_word_list" :key="index">
            <InputBlock
              :class="{ not_used: !puzzle_data.puzzle_search_list.includes(word.toUpperCase()) }"
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
      <div v-if="false" class="search_words">
        <div class="label">Search Words:</div>
        <div class="words">
          <template v-for="(word, index) in puzzle_data.puzzle_search_list" :key="index">
            <WordTile colour="'var(--vt-c-text-dark-2)'" :word="word" :delete_button="false" />
          </template>
        </div>
      </div>
    </div>

    <PuzzleGrid
      :project_name="project_name"
      :puzzle_id="puzzle_id"
      :columns="puzzle_data.columns"
      :rows="puzzle_data.rows"
      v-model="puzzle_data.cells"
      @reload="load_puzzle_data"
    />
  </div>
  <CalloutBox type="info"
    >letters highlighted
    <div class="call_out_tile"><GridTile :profane="true">A</GridTile></div>
    are part of profane words; those highlighted
    <div class="call_out_tile"><GridTile :profane="true" :profane_answer="true">A</GridTile></div>
    are also part of answers.</CalloutBox
  >
  <div class="profanity_list">
    <HeadingBlock :level="3">Profanity List</HeadingBlock>
    <template v-for="(words_and_location_list, line) in puzzle_data.profanity" :key="line">
      <div class="line_list">
        <div class="label">On {{ line }}:</div>
        <div class="profanity_words">
          <template v-for="(single_word_list, index) in words_and_location_list" :key="index">
            <div class="profanity_word">
              <WordTile
                :word="single_word_list[0] as string"
                :delete_button="false"
                colour="var(--vt-c-red-trans-bkg)"
              />
              <div v-if="single_word_list[1]">
                {{ single_word_list[1][0] === 'F' ? 'forwards' : 'reversed' }} from char
                {{ single_word_list[1][1] }} to char {{ single_word_list[1][2] }}
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
  <DividerLine :thickness="5" />
</template>

<style scoped>
.actions {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  align-items: center;
  justify-content: flex-end;
}
.line_list {
  display: flex;
}
.profanity_words {
  display: flex;
  flex-direction: column;
}
.profanity_word {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.puzzle_block_container {
  position: relative;
}
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
.call_out_tile {
  display: inline-block;
  width: 1.3rem;
  height: 1.3rem;
  margin: 0.2rem;
}
</style>
