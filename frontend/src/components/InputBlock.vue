<script setup lang="ts">
import ButtonBox from '@/components/ButtonBox.vue'

interface Props {
  type: 'float' | 'int' | 'text' | 'bool' | 'gridText'
  value?: string | number | boolean
  unit?: string
  description?: string
  withButton?: boolean
  buttonText?: string
  buttonIcon?: string
  buttonColor?: 'red' | 'indigo' | 'green' | 'orange' | 'blue' | 'yellow'
  readonly?: boolean
}

const emit = defineEmits(['pressed', 'input', 'change'])
const { readonly = false } = defineProps<Props>()
const content = defineModel<string | boolean | number>({ required: false, default: null })

const validate_text = () => {
  if (!/^[A-Za-z\s-]*$/.test(content.value.toString())) {
    content.value = content.value.toString().replace(/[^A-Za-z\s-]/g, '')
  }
  emit('input')
}

const validate_integer = () => {
  if (parseFloat(content.value.toString()) % 1 !== 0) {
    content.value = Math.round(parseFloat(content.value.toString()))
  }
  emit('input')
}
</script>

<template>
  <div class="container">
    <div class="input_container">
      <div class="label"><slot></slot></div>
      <input
        v-if="type === 'text'"
        type="text"
        class="input"
        @input="$emit('input')"
        v-model="content"
        :readonly="readonly"
      />
      <input
        v-if="type === 'gridText'"
        type="text"
        class="input"
        @input="validate_text()"
        v-model="content"
        :readonly="readonly"
      />
      <input
        v-if="type === 'float'"
        type="number"
        class="input"
        @input="$emit('input')"
        v-model="content"
        :readonly="readonly"
      />
      <input
        v-if="type === 'int'"
        type="number"
        class="input"
        @input="validate_integer()"
        step="1"
        v-model="content"
        :readonly="readonly"
      />
      <input
        v-if="type === 'bool'"
        type="checkbox"
        class="input"
        @change="$emit('change')"
        v-model="content"
        :readonly="readonly"
      />
      <div v-if="unit" class="unit">{{ unit }}</div>
      <template v-if="withButton"
        ><ButtonBox
          :icon="buttonIcon || ''"
          :colour="buttonColor || 'green'"
          :text="buttonText || 'Submit'"
          @pressed="$emit('pressed')"
      /></template>
    </div>
    <div v-if="description" class="description">
      <em>{{ description }}</em>
    </div>
  </div>
</template>

<style scoped>
.container {
  margin: 0.5rem;
  display: grid;
  grid-template-columns: auto;
  align-items: center;
  width: min-content;
}
.input_container {
  display: flex;
  align-items: center;
  justify-content: left;
}
.description {
  font-size: 0.7rem;
  align-self: center;
  justify-self: left;
  text-wrap-mode: wrap;
}
.label {
  white-space: nowrap;
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
  justify-self: left;
}
</style>
