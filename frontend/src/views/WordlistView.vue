<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, ref, watch } from 'vue'
import { useToast } from 'vue-toast-notification'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import TextBlock from '@/components/TextBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
import InputBlock from '@/components/InputBlock.vue'
import WordlistCategory from '@/components/WordlistCategory.vue'
import ButtonBox from '@/components/ButtonBox.vue'
import { useRoute, useRouter } from 'vue-router'
import type { Category, Wordlist } from '@/types/types.ts'

const props = defineProps<{ project_name: string }>()
const emit = defineEmits(['saved'])
const router = useRouter()
const loading = ref(true)
const wordlist = ref<Wordlist>({
  topic: '',
  title: '',
  creation_date: '',
  front_page_introduction: '',
  categories: [],
} as Wordlist)
const toast = useToast()
const new_category = ref<Category>({
  puzzle_topic: '',
  word_list: [],
  did_you_know: '',
  introduction: '',
} as Category)

onBeforeMount(async () => {
  await load_wordlist()
})

const load_wordlist = async () => {
  loading.value = true
  await axios
    .get(`/projects/project/${props.project_name}/wordlist/`)
    .then((response) => {
      wordlist.value = response.data
    })
    .catch(async (error) => {
      toast.error('Error getting project defaults: ' + error.message)
      console.error('Error loading project defaults:', error)
    })
  loading.value = false
}
const add_category = () => {
  if (
    new_category.value.puzzle_topic.length === 0 ||
    new_category.value.word_list.length === 0 ||
    new_category.value.introduction.length === 0 ||
    new_category.value.did_you_know.length === 0
  ) {
    toast.error('Category, word list, and both facts must be provided for new categories')
    return false
  }
  wordlist.value.categories.push(new_category.value)
  new_category.value = {
    puzzle_topic: '',
    word_list: [],
    did_you_know: '',
    introduction: '',
  } as Category
  return true
}

const save_wordlist = async () => {
  if (
    new_category.value.puzzle_topic.length > 0 ||
    new_category.value.word_list.length > 0 ||
    new_category.value.introduction.length > 0 ||
    new_category.value.did_you_know.length > 0
  ) {
    const success = add_category()
    if (!success) return
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
    <LoadingSpinner :loading="loading" />
    <HeadingBlock :level="1">Input Wordlist</HeadingBlock>
    <TextBlock>The input wordlist for project: {{ project_name }}.</TextBlock>
    <CalloutBox type="info">
      For now this is manual entry, but will become linked to the AI function.
    </CalloutBox>
    <DividerLine />
    <HeadingBlock :level="2">Base Data</HeadingBlock>
    <div class="actions">
      <ButtonBox colour="green" text="Save Changes" icon="save" @pressed="save_wordlist" />
      <ButtonBox text="Revert to Saved" colour="indigo" icon="cancel" @pressed="load_wordlist" />
    </div>
    <div class="input_list">
      <InputBlock type="text" v-model="wordlist.topic" readonly>Book Topic:</InputBlock>
      <InputBlock type="text" v-model="wordlist.title">Book Title:</InputBlock>
      <InputBlock type="text" v-model="wordlist.creation_date" readonly> Created: </InputBlock>
      <InputBlock type="textarea" v-model="wordlist.front_page_introduction"
        >Front Page Introduction:</InputBlock
      >
    </div>
    <DividerLine />
    <HeadingBlock :level="2">Categories</HeadingBlock>
    <template v-for="(category, index) in wordlist.categories" :key="index">
      <WordlistCategory
        v-model="wordlist.categories[index]"
        @remove="wordlist.categories.splice(index, 1)"
      />
    </template>
    <HeadingBlock :level="2">Add New Category</HeadingBlock>
    <WordlistCategory v-model="new_category" :adding="true" />
    <ButtonBox colour="green" text="Add Another" icon="add" @pressed="add_category" />
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
</style>
