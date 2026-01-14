<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, ref } from 'vue'
import TextBlock from '@/components/TextBlock.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ProfanityTile from '@/components/ProfanityTile.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import HeadingBlock from "@/components/HeadingBlock.vue";
import DividerLine from "@/components/DividerLine.vue";
import ButtonBox from "@/components/ButtonBox.vue";
import InputBlock from "@/components/InputBlock.vue";

const profanity_list = ref<[string]>([''])
const new_word = ref<string>('')
const new_new_word = ref<string>('')
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
      v-model:text="new_word"
      :withButton="true"
      buttonText="Add Word"
    description="A new word to add to the profanity list.  Words may only contain alphabetic characters [A-Z] or space ` ` or hyphen `-`.  Numbers and other punctuation are prevented from input.">Add a new word to the list:</InputBlock>
    <CalloutBox type="warning" v-if="new_word.length > 0 && profanity_list.includes(new_word.toUpperCase().replace(/[\s-]/g, ''))">
      Word is already in the profanity list.
    </CalloutBox>
    <DividerLine />
    <HeadingBlock :level="2">Profanity List</HeadingBlock>
    <CalloutBox type="critical">Deleting items from the list cannot be undone. They will need to be manually added back in.</CalloutBox>
    <div class="profanty_list">
      <div class="profanity_word" v-for="(word, index) in profanity_list" :key="index">
        <ProfanityTile :word="word" @modal="loading = true" @reload="load_list()" />
      </div>
    </div>
  </div>
</template>

<style scoped>




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
