<script setup lang="ts">
import { useIntervalFn, useWebSocket } from '@vueuse/core'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import type { AICommand, AIResponse, Category, Wordlist, WordlistInput } from '@/types/types.ts'
import axios from 'axios'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import TextBlock from '@/components/TextBlock.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import DividerLine from '@/components/DividerLine.vue'
import ButtonBox from '@/components/ButtonBox.vue'
import InputBlock from '@/components/InputBlock.vue'
import WordlistCategory from '@/components/WordlistCategory.vue'

const props = defineProps<{ project_name: string }>()
const emit = defineEmits(['saved'])
const router = useRouter()
const loading = ref(false)
const toast = useToast()
const wordlist = ref<Wordlist>()
const main_topic = ref<string>('')
const number_of_puzzles = ref<number>(0)
const entries_per_puzzle = ref<number>(0)
const subtopic_list = ref<string[]>([])
const ai_state = ref<'OPEN' | 'CLOSED' | 'THINKING'>('OPEN')
const topic_to_add = ref('')

const make_message = (command: string): AICommand => {
  if (['ping', 'create', 'puzzles'].includes(command)) {
    return {
      command: command,
      main_topic: main_topic.value,
      number_of_puzzles: number_of_puzzles.value,
      entries_per_puzzle: entries_per_puzzle.value,
      subtopic_list: subtopic_list.value,
    } as AICommand
  }
  throw new Error(`Unknown command: ${command}`)
}

const { status, data, send, open, close, ws } = useWebSocket(
  `ws://localhost:5000/projects/project/Pepper/wordlist/ws`,
  {
    autoReconnect: true,
    heartbeat: {
      message: JSON.stringify(make_message('ping')),
      scheduler: (cb) => useIntervalFn(cb, 10000),
      pongTimeout: 10000,
    },
    onMessage: (ws, event) => update_data(event.data),
  },
)

const send_message = (command: string) => {
  send(JSON.stringify(make_message(command)))
}

const update_data = (data: string) => {
  const response = JSON.parse(data) as AIResponse
  switch (response.response) {
    case 'pong':
      return
    case 'error':
      toast.error(response.payload.message as string)
      return
    case 'thinking':
      ai_state.value = 'THINKING'
      loading.value = true
      return
    case 'not_thinking':
      ai_state.value = status.value === 'OPEN' ? 'OPEN' : 'CLOSED'
      loading.value = false
      return
    case 'topic_list':
      if (!response.payload.base_data) {
        toast.error('Ahhgghg received topic_list response without the correct data')
        return
      }
      let base_data = response.payload.base_data as WordlistInput
      wordlist.value = {
        topic: base_data.topic,
        title: base_data.title,
        creation_date: base_data.creation_date,
        front_page_introduction: base_data.front_page_introduction,
        categories: [],
      }
      subtopic_list.value = base_data.subtopic_list
      return
    case 'puzzle':
      if (!response.payload.puzzle) {
        toast.error('Ahhgghg received puzzle response without the correct data')
        return
      }
      if (!wordlist.value) {
        toast.error('Ahhgghg received puzzle response before topic_list')
        return
      }
      let puzzle = response.payload.puzzle as Category
      wordlist.value.categories.push(puzzle)
      return
    default:
      toast.error(`Unknown response: ${response.response}`)
  }
}
watch(status, (new_status) => {
  ai_state.value = new_status === 'OPEN' ? 'OPEN' : 'CLOSED'
})

const create_base_data = async () => {
  if (!main_topic.value) {
    toast.error('Please enter a main topic')
    return
  }
  if (number_of_puzzles.value < 1 || entries_per_puzzle.value < 4) {
    toast.error('Please enter a positive number of puzzles and entries per puzzle')
    return
  }
  send_message('create')
}

const add_topic = (topic: string) => {
  subtopic_list.value.push(topic)
  topic_to_add.value = ''
}

const create_puzzles = async () => {
  if (entries_per_puzzle.value < 4) {
    toast.error('Please enter a positive number of puzzles and entries per puzzle')
    return
  }
  if (subtopic_list.value.length === 0) {
    toast.error('Please enter at least one subtopic')
    return
  }
  send_message('puzzles')
}

const save_wordlist = async () => {
  if (!wordlist.value) {
    toast.error('Wordlist not loaded yet')
    return
  }
  if (
    wordlist.value.categories.some(
      (category) =>
        category.puzzle_topic.length === 0 ||
        category.word_list.length === 0 ||
        category.introduction.length === 0 ||
        category.did_you_know.length === 0,
    )
  ) {
    toast.error('All categories must have a name, word list, and both facts')
    return
  }
  loading.value = true
  await axios
    .post(`/projects/project/${props.project_name}/wordlist`, wordlist.value)
    .then(async () => {
      toast.success('Wordlist saved successfully')
      await router.push({
        name: 'edit-wordlist',
        params: { project_name: props.project_name },
      })
    })
    .catch((error) => {
      toast.error('Error saving wordlist' + error.message)
    })
  emit('saved')
  loading.value = false
}
</script>

<template>
  <div class="card">
    <HeadingBlock :level="1">Creating Input Wordlist</HeadingBlock>
    <TextBlock>The input wordlist for project: {{ project_name }}.</TextBlock>
    <CalloutBox type="warning">
      <TextBlock>
        This creation function is reliant on having an internet connection and an API key for the
        chosen model. Please ensure you have these before proceeding.
      </TextBlock>
      <TextBlock>
        Changes are not saved until you hit the save button. Navigating away will clear the form and
        lose any changes made.
      </TextBlock>
    </CalloutBox>
    <DividerLine />
    <div class="seed_block_container">
      <LoadingSpinner :loading="loading" local/>
      <HeadingBlock :level="2">Seed Data</HeadingBlock>
      <div class="actions">
        <ButtonBox :colour="status === 'OPEN' ? 'green' : 'red'" :text="`AI State: ${ai_state}`" />
      </div>
      <div class="input_list">
        <InputBlock type="text" v-model="main_topic">Main Topic:</InputBlock>
        <InputBlock type="int" v-model="number_of_puzzles">Number of Puzzles:</InputBlock>
        <InputBlock type="int" v-model="entries_per_puzzle">Words per Puzzle:</InputBlock>
      </div>
      <div v-if="!wordlist" class="actions">
        <ButtonBox
          colour="green"
          text="Create Subtopics"
          icon="mindfulness"
          @pressed="create_base_data"
        />
      </div>
      <template v-if="subtopic_list.length > 0 && wordlist && wordlist.categories.length === 0">
        <div>
          <CalloutBox type="info">
            <TextBlock>
              Edit these sub topic until you are satisfied and then click create puzzles.
            </TextBlock>
          </CalloutBox>
          <template v-for="(_, index) in subtopic_list" :key="index">
            <InputBlock
              type="text"
              v-model="subtopic_list[index]"
              withButton
              buttonIcon="delete"
              buttonColor="red"
              @pressed="subtopic_list.splice(index, 1)"
            />
          </template>
          <InputBlock
            buttonIcon="add"
            type="text"
            v-model="topic_to_add"
            :withButton="true"
            buttonText="Add"
            buttonColor="green"
            @pressed="add_topic"
          >
            Add Word
          </InputBlock>
        </div>
        <div v-if="wordlist && wordlist.categories.length === 0" class="actions">
          <ButtonBox
            colour="green"
            text="Create Puzzles"
            icon="mindfulness"
            @pressed="create_puzzles"
          />
        </div>
      </template>
    </div>
    <DividerLine />
    <div>
    <template v-if="wordlist">
      <HeadingBlock :level="2">Base Data</HeadingBlock>
      <div class="actions">
        <ButtonBox v-if="wordlist && wordlist.categories.length > 0 && !loading" colour="green" text="Save Changes" icon="save" @pressed="save_wordlist" />
      </div>
      <div class="input_list">
        <InputBlock type="text" v-model="wordlist.topic" readonly>Book Topic:</InputBlock>
        <InputBlock type="text" v-model="wordlist.title">Book Title:</InputBlock>
        <InputBlock type="text" v-model="wordlist.creation_date" readonly> Created: </InputBlock>
        <InputBlock type="textarea" v-model="wordlist.front_page_introduction">
          Front Page Introduction:
        </InputBlock>
      </div>
      <DividerLine />
      <HeadingBlock :level="2">Categories</HeadingBlock>
      <template v-for="(category, index) in wordlist.categories" :key="index">
        <WordlistCategory
          v-model="wordlist.categories[index]"
          @remove="wordlist.categories.splice(index, 1)"
        />
      </template>
    </template>
  </div>
  </div>
</template>

<style scoped>
.input_list {
  display: flex;
  flex-direction: column;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.seed_block_container {
  position: relative;
}
</style>
