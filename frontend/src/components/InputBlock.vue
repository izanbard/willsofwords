<script setup lang="ts">
import ButtonBox from '@/components/ButtonBox.vue'

interface Props {
  type: 'float' | 'int' | 'text' | 'bool' | 'gridText' | 'textarea'
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
const content = defineModel<string | number | readonly string[] | null | undefined>({
  required: false,
  default: null,
})

const validate_text = () => {
  if (content.value && !/^[A-Za-z\s-]*$/.test(content.value.toString())) {
    content.value = content.value.toString().replace(/[^A-Za-z\s-]/g, '')
  }
  emit('input')
}

const validate_integer = () => {
  if (content.value && parseFloat(content.value.toString()) % 1 !== 0) {
    content.value = Math.round(parseFloat(content.value.toString()))
  }
  emit('input')
}
</script>

<template>
  <div class="container">
    <div class="input_container">
      <div class="label"><slot></slot></div>
      <textarea
        v-if="type === 'textarea'"
        class="input"
        @input="$emit('input')"
        v-model="content"
        :readonly="readonly"
      ></textarea>
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
          :text="buttonText"
          @pressed="$emit('pressed')"
      /></template>
    </div>
    <div v-if="description" class="description">
      <div>
        <em>{{ description }}</em>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  margin: 0.5rem;
  display: inline-block;
}
.input_container {
  display: flex;
  align-items: center;
  justify-content: left;
  gap: 0.5rem;
}
.description {
  font-size: 0.7rem;
  display: flex;
}
.description div {
  flex-grow: 1;
  width: 0;
  word-break: break-word;
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
}
textarea {
  resize: both;
  field-sizing: content;
  white-space: pre-line;
  min-width: 10rem;
}
</style>
