<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, ref, onBeforeUnmount, onMounted } from 'vue'
import TextBlock from '@/components/TextBlock.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import WordTile from '@/components/WordTile.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
import InputBlock from '@/components/InputBlock.vue'
import { useToast } from 'vue-toast-notification'

const profanity_list = ref<[string]>([''])
const new_word = ref<string>('')
const loading = ref<boolean>(true)
const toast = useToast()

const load_list = async () => {
  await axios
    .get('/settings/profanity/')
    .then((response) => {
      profanity_list.value = response.data.word_list
    })
    .catch((error) => {
      console.error('Error loading profanity list:', error)
      loading.value = false
    })
  loading.value = false
}

onBeforeMount(async () => {
  await load_list()
})
onMounted(() => {
  const curse_audio = document.getElementById('curse_audio') as HTMLAudioElement
  curse_audio.play()
})
onBeforeUnmount(() => {
  toast.clear()
})

const add_word = async () => {
  if (new_word.value.length === 0) {
    toast.warning('Word cannot be empty')
    return
  }
  if (profanity_list.value.includes(new_word.value.toUpperCase().replace(/[\s-]/g, ''))) {
    toast.info('Word already exists in profanity list')
    return
  }
  loading.value = true
  await axios
    .put('/settings/profanity/', null, { params: { word: new_word.value } })
    .catch((error) => {
      toast.error('Error adding word to profanity list: ' + error.message)
      console.error('Error loading profanity list:', error)
      loading.value = false
    })
  new_word.value = ''
  await load_list()
}
const remove_word = async (word: string) => {
  await axios.delete('/settings/profanity/', { params: { word: word } })
  await load_list()
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <HeadingBlock :level="1">Manage the Profanity List Contents</HeadingBlock>
    <TextBlock>
      This is the list of profane words that the application uses to filter out inappropriate
      content. The same list is used for validating input and validating the puzzle grids.
    </TextBlock>
    <CalloutBox type="info">
      Note changes to this list should be back ported to the repository so they are not lost if
      re-installation is required.
    </CalloutBox>
    <DividerLine />
    <HeadingBlock :level="2">Add New Word to List</HeadingBlock>
    <InputBlock
      type="gridText"
      @pressed="add_word"
      v-model="new_word"
      :withButton="true"
      buttonText="Add Word"
      buttonIcon="add"
      description="A new word to add to the profanity list.  Words may only contain alphabetic characters [A-Z] or space ` ` or hyphen `-`.  Numbers and other punctuation are prevented from input."
    >
      Add a new word to the list:
    </InputBlock>
    <CalloutBox
      type="warning"
      v-if="
        new_word.length > 0 && profanity_list.includes(new_word.toUpperCase().replace(/[\s-]/g, ''))
      "
    >
      Word is already in the profanity list.
    </CalloutBox>
    <DividerLine />
    <HeadingBlock :level="2">Profanity List</HeadingBlock>
    <div class="profanity_list">
      <div class="profanity_word" v-for="(word, index) in profanity_list" :key="index">
        <WordTile :word="word" @delete="remove_word" />
      </div>
    </div>
  </div>
  <template>
    <audio id="curse_audio">
      <source src="/audio/curses.m4a" type="audio/mp4" />
    </audio>
  </template>
</template>

<style scoped>
.profanity_list {
  column-width: 250px;
  column-gap: 1rem;
  column-rule: 1px solid var(--vt-c-divider-light-1);
  margin: 0;
}

.profanity_word {
  display: block;
  width: 100%;
  break-inside: avoid;
  padding-top: 0.01rem;
}
</style>
