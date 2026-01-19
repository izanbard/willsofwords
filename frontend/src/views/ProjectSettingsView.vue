<script setup lang="ts">
import axios from 'axios'
import { onBeforeMount, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import TextBlock from '@/components/TextBlock.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import DividerLine from '@/components/DividerLine.vue'
import InputBlock from '@/components/InputBlock.vue'
import ButtonBox from '@/components/ButtonBox.vue'

defineProps<{ create: 'defaults' | 'new' | 'edit' }>()
const router = useRouter()
const projectDefaults = ref({})
const toast = useToast()
const loading = ref<boolean>(true)
const project_name = ref<string>('')

const load_defaults = async () => {
  await axios
    .get('/settings/project-defaults/')
    .then((response) => {
      projectDefaults.value = response.data
    })
    .catch((error) => {
      toast.error('Error getting project defaults: ' + error.message)
      console.error('Error loading project defaults:', error)
    })
  loading.value = false
}

const update_defaults = async () => {
  loading.value = true
  await axios.patch('/settings/project-defaults/', projectDefaults.value).catch((error) => {
    toast.error('Error updating default: ' + error.message)
    console.error('Error updating default:', error)
  })
  await load_defaults()
}

const save_new_project = async () => {
  loading.value = true
  await axios
    .post('/projects/', { name: project_name.value, settings: projectDefaults.value })
    .catch((error) => {
      toast.error('Error creating project: ' + error.message)
      console.error('Error creating project:', error)
    })
  router.push({ name: 'projects' })
}

onBeforeMount(async () => {
  await load_defaults()
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
  dpi: 'Dots per inch for printing',
  debug: 'Enable Printdebug mode to see print margins in pdf',
  page_height_inches: 'the edge to edge height of the page',
  page_width_inches: 'the edge to edge width of the page',
  top_margin_inches:
    'the top margin of the page. KDP minimum value is 0.25 - this is not validated',
  bottom_margin_inches:
    'the bottom margin of the page. KDP minimum value is 0.25 - this is not validated',
  outer_margin_inches:
    'the outer margin of the page the not gutter. KDP minimum value is 0.25 - this is not validated',
  inner_margin_inches:
    'the inner margin of the page - the gutter. KDP minimum value is 0.25 - this is not validated',
  title_box_height_inches: 'the height from the margin to contain the puzzle title',
  wordlist_box_height_inches:
    'the height from the margin to contain the wordlist in single page layout',
  wordlist_font_size_inches:
    ' the fontsize of the word list.  The system may reduce this font to fit the words in',
  wordlist_line_spacing_inches: 'the line spacing between words in the wordlist',
  grid_pad_inches: 'the minimum padding outside the border of the grid. Should be 0.',
  grid_border_inches: 'the thickness of the grid border line',
  grid_border_radius_inches:
    'the rounded corners radius for the border line, higher numbers make more pronounced curve',
  grid_margin_inches: 'the space between the grid and the border',
  cell_font_size_inches: 'the size of the font for the characters in the cell',
  min_cell_size_factor:
    'the amount to multiply the font size by to get the minimum cell size.  large number is more space round the individual letters of the grid',
  variable_cell_size:
    'if true, the cell size will vary from puzzle to puzzle between min cells size and max cell size',
  max_cell_size_factor:
    'the amount to multiply the font size by to get the maximum cell size.  large number is more space round the individual letters of the grid',
  long_fact_heading_font_size_inches:
    'the font size for the fact title in long form (double page layout)',
  long_fact_content_font_size_inches:
    'the font size for the fact content in long form (double page layout)',
  long_fact_line_spacing_inches:
    'the line spacing between lines in the fact content in long form (double page layout)',
  page_number_font_size_inches: 'the font size for the page number',
  page_number_offset_inches: 'the offset from the bottom right corner of the margins',
  solution_page_cols: 'the number of columns in the solution page',
  solution_page_rows: 'the number of rows in the solution page',
  max_density: 'the maximum density of the grid.  Higher numbers are more dense',
  min_density: 'the minimum density of the grid.  Lower numbers are more sparse',
  max_placement_attempts:
    'the maximum number of attempts to place a word in the grid before giving up',
  enable_profanity_filter: 'enable profanity filter during puzzle creation',
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <template v-if="create === 'new'">
      <HeadingBlock :level="1">Create New Project</HeadingBlock>
      <InputBlock type="text" v-model="project_name">Project Name: </InputBlock>
      <ButtonBox
        icon="folder_copy"
        text="Create Project"
        colour="green"
        @pressed="save_new_project()"
      />
    </template>
    <template v-if="create === 'defaults'">
      <HeadingBlock :level="1">Project Defaults</HeadingBlock>
      <TextBlock>These are the project defaults used to set up a new project.</TextBlock>
      <CalloutBox type="info">
        Note changes to this list should be back ported to the repository so they are not lost if
        re-installation is required.
      </CalloutBox>
    </template>
    <DividerLine />
    <template v-if="create === 'new'">
      <HeadingBlock :level="2">Project Settings</HeadingBlock>
      <TextBlock
        >These settgins will be saved in the project folder. They may be changed later.</TextBlock
      >
    </template>
    <template v-if="create === 'defaults'">
      <HeadingBlock :level="2">Manage Defaults</HeadingBlock>
      <ButtonBox icon="save" @pressed="update_defaults()" colour="green" text="Save Changes" />
    </template>
    <div class="project_defaults">
      <InputBlock
        v-for="(value, mykey) in projectDefaults"
        :key="mykey"
        :type="typeLookup[typeof value] || 'text'"
        v-model="projectDefaults[mykey]"
        :description="descriptions[mykey]"
      >
        {{ mykey }}:
      </InputBlock>
    </div>
    <template v-if="create === 'new'">
      <ButtonBox
        icon="folder_copy"
        text="Create Project"
        colour="green"
        @pressed="save_new_project()"
      />
    </template>
    <template v-if="create === 'defaults'">
      <ButtonBox icon="save" @pressed="update_defaults()" colour="green" text="Save Changes" />
    </template>
  </div>
</template>

<style scoped>
.project_defaults {
  display: flex;
  flex-direction: column;
  justify-self: flex-start;
  align-items: flex-end;
}
</style>
