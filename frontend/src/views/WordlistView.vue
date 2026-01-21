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
import { useRouter, useRoute } from 'vue-router'

export interface Category {
  category: string
  word_list: string[]
  short_fact: string
  long_fact: string
}

interface Wordlist {
  title: string
  category_prompt: string
  wordlist_prompt: string
  creation_date: string
  category_list: Category[]
}

const props = defineProps<{ project_name: string; mode?: 'create' | 'edit' }>()
const emit = defineEmits(['saved'])
const router = useRouter()
const route = useRoute()
const loading = ref(true)
const wordlist = ref<Wordlist>({
  title: '',
  category_prompt: '',
  wordlist_prompt: '',
  creation_date: '',
  category_list: [],
} as Wordlist)
const toast = useToast()
const new_category = ref<Category>({
  category: '',
  word_list: [],
  short_fact: '',
  long_fact: '',
} as Category)

const create_wordlist_according_to_mode = async () => {
  if (props.mode !== 'create') {
    await load_wordlist()
    return
  }
  loading.value = false
}

onBeforeMount(async () => {
  await create_wordlist_according_to_mode()
})

const load_wordlist = async () => {
  loading.value = true
  await axios
    .get(`/projects/project/${props.project_name}/wordlist`)
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
    new_category.value.category.length === 0 ||
    new_category.value.word_list.length === 0 ||
    new_category.value.long_fact.length === 0 ||
    new_category.value.short_fact.length === 0
  ) {
    toast.error('Category, word list, and both facts must be provided for new categories')
    return false
  }
  wordlist.value.category_list.push(new_category.value)
  new_category.value = { category: '', word_list: [], short_fact: '', long_fact: '' } as Category
  return true
}

const save_wordlist = async () => {
  if (
    new_category.value.category.length > 0 ||
    new_category.value.word_list.length > 0 ||
    new_category.value.long_fact.length > 0 ||
    new_category.value.short_fact.length > 0
  ) {
    let success = add_category()
    if (!success) return
  }
  if (
    wordlist.value.category_list.some(
      (category) =>
        category.category.length === 0 ||
        category.word_list.length === 0 ||
        category.long_fact.length === 0 ||
        category.short_fact.length === 0,
    )
  ) {
    toast.error('All categories must have a name, word list, and both facts')
    return
  }
  loading.value = true
  await axios
    .post(`/projects/project/${props.project_name}/wordlist`, wordlist.value)
    .then(async (response) => {
      toast.success('Wordlist saved successfully')
      await router.push({
        name: 'edit-wordlist',
        params: { project_name: props.project_name, mode: 'edit' },
      })
    })
    .catch((error) => {
      toast.error('Error saving wordlist' + error.message)
    })
  emit('saved')
  loading.value = false
}

watch(
  () => route.params.mode,
  async (mode) => {
    if (mode === 'edit') {
      await load_wordlist()
    } else {
      wordlist.value = {
        title: '',
        category_prompt: '',
        wordlist_prompt: '',
        creation_date: '',
        category_list: [],
      } as Wordlist
    }
  },
)
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
      <ButtonBox
        v-if="mode === 'edit'"
        text="Revert to Saved"
        colour="indigo"
        icon="cancel"
        @pressed="load_wordlist"
      />
    </div>
    <div class="input_list">
      <InputBlock type="text" v-model="wordlist.title">Book Title:&nbsp;</InputBlock>
      <InputBlock
        type="text"
        v-model="wordlist.creation_date"
        description="Not ued for now, but will form aprt of the AI audit process.  Feel free to leave it blank or otherwise unmolested."
        >Created:&nbsp;
      </InputBlock>
      <InputBlock
        type="text"
        v-model="wordlist.wordlist_prompt"
        description="Not currently used, here for future proofing the AI component."
        >Prompt to Generate Categories:&nbsp;</InputBlock
      >
      <InputBlock
        type="text"
        v-model="wordlist.category_prompt"
        description="Not currently used, here for future proofing the AI component."
        >Prompt to Generate Puzzle Words:&nbsp;</InputBlock
      >
    </div>
    <DividerLine />
    <HeadingBlock :level="2">Categories</HeadingBlock>
    <template v-for="(category, index) in wordlist.category_list">
      <WordlistCategory v-model="wordlist.category_list[index]" />
    </template>
    <HeadingBlock :level="2">Add New Category</HeadingBlock>
    <WordlistCategory v-model="new_category" />
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
