<script setup lang="ts">
import InputBlock from '@/components/InputBlock.vue'
import TextBlock from '@/components/TextBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
import type { Category } from '@/views/WordlistView.vue'
import { ref } from 'vue'
import ButtonBox from '@/components/ButtonBox.vue'

const {adding = false} = defineProps<{ adding?: boolean }>()
const category = defineModel<Category>({ required: false, default: null })
defineEmits(['remove'])
const word_to_add = ref('')

const addWord = () => {
  if (word_to_add.value.trim() === '') return
  word_to_add.value
    .trim()
    .split(/\s*,\s*/)
    .forEach((word) => {
      category.value.word_list.push(word)
    })
  word_to_add.value = ''
}
</script>

<template>
  <div class="category">
    <div class="actions">
    <ButtonBox v-if="!adding" colour="red" text="Remove Category" icon="delete" @pressed="$emit('remove')" />
    </div>
    <InputBlock type="text" v-model="category.category">Title:&nbsp;</InputBlock>
    <div class="input_list">
      <InputBlock type="textarea" v-model="category.short_fact">Short Form Fact:&nbsp;</InputBlock>
      <InputBlock type="textarea" v-model="category.long_fact">Long Form Fact:&nbsp;</InputBlock>
    </div>
    <div class="wordlist">
      <TextBlock class="label">Words in this category:</TextBlock>
      <div>
        <template v-for="(_, index) in category.word_list" :key="index">
          <InputBlock
            type="text"
            v-model="category.word_list[index]"
            withButton
            buttonIcon="delete"
            buttonColor="red"
            @pressed="category.word_list.splice(index, 1)"
          />
        </template>
        <InputBlock
          buttonIcon="add"
          type="text"
          v-model="word_to_add"
          :withButton="true"
          buttonText="Add"
          buttonColor="green"
          @pressed="addWord"
        >
          Add Word
        </InputBlock>
      </div>
    </div>
    <DividerLine :thickness="1" />
  </div>
</template>

<style scoped>
.input_list {
  display: flex;
  flex-direction: column;
}
.label {
  white-space: nowrap;
}
.wordlist {
  display: flex;
}
.actions {
  display: flex;
  justify-content: flex-end;
}
</style>
