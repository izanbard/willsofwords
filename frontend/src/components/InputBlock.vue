<script setup lang="ts">
import ButtonBox from "@/components/ButtonBox.vue";
const emit = defineEmits(['pressed', 'input', 'change'])
defineProps<{
  type: 'float'|'int'|'text'|'bool'|'gridText',
  unit?: string,
  description?: string,
  withButton?: boolean,
  buttonText?: string
}>()
const text_content = defineModel<string>('text',{required: false, default: ''})
const number_content = defineModel<number>('number',{required: false, default: 0})

const validate_text = () => {
  if (!/^[A-Za-z\s-]*$/.test(text_content.value)) {
    text_content.value = text_content.value.replace(/[^A-Za-z\s-]/g, '')
  }
  emit('input')
}

const validate_integer = () => {
  if (number_content.value % 1 !== 0) {
    number_content.value = Math.round(number_content.value)
  }
  emit('input')
}
</script>

<template>
<div>
  <span class="label"><slot></slot></span>
  <input v-if="type==='text'" type="text" class="input" @input="$emit('input')" v-model="text_content"/>
  <input v-if="type==='gridText'" type="text" class="input" @input="validate_text()" v-model="text_content"/>
  <input v-if="type==='float'" type="number" class="input" @input="$emit('input')" v-model="number_content"/>
  <input v-if="type==='int'" type="number" class="input" @input="validate_integer()" step="1" v-model="number_content"/>
  <input v-if="type==='bool'" type="checkbox" class="input" @change="$emit('change')" v-model="number_content"/>
  <span v-if="unit" class="unit">{{ unit }}</span>
  <span v-if="withButton"><ButtonBox colour="green" :text="buttonText || 'Submit'" @pressed="$emit('pressed')" /></span>
  <div v-if="description" class="description"><em>{{ description }}</em></div>
</div>
</template>

<style scoped>
.description {
  font-size: 0.7rem;
}
.input:focus {
  outline: none;
}

.input {
  background-color: var(--color-background-wow);
  border: var(--color-border) solid 2px;
  border-radius: 0.5rem;
  padding: 0.3rem;
  font-size: 1rem;
}
</style>
