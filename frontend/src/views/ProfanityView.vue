<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, ref } from 'vue'
import TextBlock from '@/components/TextBlock.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ProfanityTile from '@/components/ProfanityTile.vue'
import CalloutBox from '@/components/CalloutBox.vue'

const profanity_list = ref<[string]>([''])
const new_word = ref<string>('')
const loading = ref<boolean>(true)

const load_list = async () => {
  await axios.get('/settings/profanity/').then((response) => {
    profanity_list.value = response.data.word_list
  })
  loading.value = false
}

onBeforeMount(async () => {
    await load_list()
})

const validate_word = () => {
  if (!/^[A-Za-z\s-]*$/.test(new_word.value)) {
    new_word.value = new_word.value.replace(/[^A-Za-z\s-]/g, '')
  }
}

const add_word = async () => {
  if (profanity_list.value.includes(new_word.value.toUpperCase().replace(/[\s-]/g, ''))) {
    return
  }
  loading.value = true
  await axios.put('/settings/profanity/', null, { params: { word: new_word.value } })
  new_word.value = ''
  await load_list()
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <h1>Manage the Profanity List Contents</h1>
    <TextBlock>
      This is the list of profane words that the application uses to filter out inappropriate
      content. The same list is used for validating input and validating the puzzle grids.
    </TextBlock>
    <CalloutBox type="info">
      Note changes to this list should be back ported to the repository so they are not lost if
      re-installation is required.
    </CalloutBox>
    <hr />
    <h2>Add New Word to List</h2>
    <TextBlock>
      Add a new word to the list:
      <input class="text_input" type="text" v-model.trim="new_word" @input="validate_word()" />
      <span class="button" @click="add_word()">Submit</span>
    </TextBlock>
    <CalloutBox type="warning" v-if="new_word.length > 0 && profanity_list.includes(new_word.toUpperCase().replace(/[\s-]/g, ''))">
      Word is already in the profanity list.
    </CalloutBox>
    <CalloutBox type="warning">Words may only contain alphabetic characters [A-Z] or ` ` or `-`.  Numbers and other punctuation are prevented from input.</CalloutBox>
    <hr />
    <h2>Profanity List</h2>
    <CalloutBox type="critical">Deleting items from the list cannot be undone. They will need to be manually added back in.</CalloutBox>
    <div class="profanty_list">
      <div class="profanity_word" v-for="(word, index) in profanity_list" :key="index">
        <ProfanityTile :word="word" @modal="loading = true" @reload="load_list()" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.button {
  background-color: var(--vt-c-red-muted);
  border-radius: 0.5rem;
  padding: 0.2rem;
  cursor: pointer;
  color: var(--vt-c-white);
  border: var(--color-border) solid 2px;
  font-size: 1rem;
}

.text_input:focus {
  outline: none;
}

.text_input {
  background-color: var(--color-background-wow);
  border: var(--color-border) solid 2px;
  border-radius: 0.5rem;
  padding: 0.3rem;
  font-size: 1rem;
}

hr {
  border: 0;
  border-top: 1px solid var(--vt-c-divider-light-1);
  margin: 1rem 0;
}

h1,
h2 {
  margin: 0.5rem 0;
  color: var(--color-heading);
  font-weight: bold;
  font-family: 'Verdana Bold', sans-serif;
}

h1 {
  font-size: 1.6rem;
}

h2 {
  font-size: 1.2rem;
}

.profanty_list {
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
