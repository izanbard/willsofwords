<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, onBeforeUnmount, ref } from 'vue'
import { useToast } from 'vue-toast-notification'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import DividerLine from '@/components/DividerLine.vue'
import TextBlock from '@/components/TextBlock.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import InputBlock from '@/components/InputBlock.vue'

const appConfig = ref({})
const toast = useToast()
const loading = ref<boolean>(true)

const load_config = async () => {
  await axios
    .get('/settings/app-config/')
    .then((response) => {
      appConfig.value = response.data
    })
    .catch((error) => {
      toast.error('Error getting app config: ' + error.message)
      console.error('Error loading app config:', error)
    })
  loading.value = false
}

onBeforeMount(async () => {
  await load_config()
})
onBeforeUnmount(() => {
  toast.clear()
})
const typeLookup: Record<string, 'float' | 'int' | 'text' | 'bool' | 'gridText'> = {
  string: 'text',
  number: 'float',
  boolean: 'bool',
  bigint: 'int',
  symbol: 'text',
  object: 'text',
  function: 'text',
  undefined: 'text',
}
const descriptions: Record<string, string> = {
  log_level: 'level of log output generated',
  input_filename: 'the default file name for the wordlist input',
  data_filename: 'the default file name for the puzzle data output',
  output_filename:
    'the default file name for the manuscript output.  If print debug id true the, it is appended with _PRINT_DEBUG',
  frontend_host_for_cors:
    'the url in the browser for sone looking at the front end this is to permit a poke through on the CORS security shield.',
  model: 'the name of the model being used',
  host: 'the url to the ollama instance',
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <HeadingBlock :level="1">App Config</HeadingBlock>
    <TextBlock
      >These are the App Config Settings used under te hood. This list s read only - to make change
      look in the `.env` file or the `docker-compose.yaml` file.</TextBlock
    >
    <DividerLine />
    <HeadingBlock :level="2">App Section</HeadingBlock>
    <div class="config">
      <InputBlock
        v-for="(value, mykey) in appConfig.app"
        :key="mykey"
        :type="typeLookup[typeof value] || 'text'"
        v-model="appConfig.app[mykey]"
        :description="descriptions[mykey]"
        :readonly="true"
        >{{ mykey }}:
      </InputBlock>
    </div>
    <DividerLine />
    <HeadingBlock :level="2">AI Section</HeadingBlock>
    <TextBlock>Not currently used.</TextBlock>
    <div class="config">
      <InputBlock
        v-for="(value, mykey) in appConfig.ai"
        :key="mykey"
        :type="typeLookup[typeof value] || 'text'"
        v-model="appConfig.ai[mykey]"
        :description="descriptions[mykey]"
        :readonly="true"
        >{{ mykey }}:
      </InputBlock>
    </div>
  </div>
</template>

<style scoped>
.config {
  display: flex;
  flex-direction: column;
  justify-self: flex-start;
  align-items: flex-end;
}
</style>
