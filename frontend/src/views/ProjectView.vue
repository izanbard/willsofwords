<script setup lang="ts">
import axios from 'axios'
import HeadingBlock from '@/components/HeadingBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
import { onBeforeMount, onBeforeUnmount, onMounted, ref } from 'vue'
import { useToast } from 'vue-toast-notification'
import ProjectFile from '@/components/ProjectFile.vue'
import { useRouter } from 'vue-router'
import InputBlock from '@/components/InputBlock.vue'

const { project_name } = defineProps<{ project_name: string; mode: string }>()

let reloader: number | undefined

const file_list = ref<{ name: string; project_files: [{ name: string; modified_date: string }] }>()
const loading = ref<boolean>(true)
const toast = useToast()
const router = useRouter()
const print_debug = ref<boolean>(false)

enum file_state_enum {
  exists = 'exists',
  not_exists = 'not_exists',
  creating = 'creating',
}
enum hero_files {
  project_settings = 'project_settings.json',
  wordlist = 'wordlist.json',
  puzzledata = 'puzzledata.json',
  manuscript = 'manuscript.pdf',
}

const named_file_state = (named_file: string) => {
  if (file_list.value?.project_files) {
    for (const file of file_list.value?.project_files) {
      if (file.name === named_file) {
        return [file_state_enum.exists, 0]
      }
      if (file.name.startsWith(named_file) && file.name.endsWith('.marker')) {
        const mynumber = parseInt(
          file.name.replace('.marker', '').replace(named_file, '').replace('.', ''),
        )
        return [file_state_enum.creating, mynumber]
      }
    }
  }
  return [file_state_enum.not_exists, 0]
}

const load_project_file_list = async () => {
  await axios
    .get('/projects/project/' + project_name + '/')
    .then((response) => {
      file_list.value = response.data
      loading.value = false
    })
    .catch(() => {
      toast.error('Failed to load project list')
      loading.value = false
    })
}

const file_in_hero_list = (filename: string) => {
  const options: string[] = Object.values(hero_files)
  return !options.includes(filename) && !filename.endsWith('.marker')
}

onBeforeMount(async () => {
  await load_project_file_list()
})

onMounted(() => {
  reloader = setInterval(async () => {
    await load_project_file_list()
  }, 2000)
})

onBeforeUnmount(() => {
  toast.clear()
  if (reloader) {
    clearInterval(reloader)
  }
})
const edit_project_settings = () => {
  router.push({
    name: 'edit-project-settings',
    params: { project_name: project_name, mode: 'edit' },
  })
}
const edit_wordlist = () => {
  router.push({
    name: 'edit-wordlist',
    params: { project_name: project_name, mode: 'edit' },
  })
}
const create_wordlist = () => {
  router.push({
    name: 'create-wordlist',
    params: { project_name: project_name },
  })
}
const delete_wordlist = async () => {
  await axios
    .delete(`/projects/project/${project_name}/wordlist`)
    .then(async () => {
      create_wordlist()
      await load_project_file_list()
    })
    .catch((error) => {
      toast.error('Error deleting wordlist:', error.message)
    })
}
const edit_puzzledata = () => {
  router.push({
    name: 'edit-puzzledata',
    params: { project_name: project_name },
  })
}
const create_puzzledata = async () => {
  await axios
    .post(`/projects/project/${project_name}/puzzledata`)
    .then(async () => {
      toast.success('Background job for puzzle data creation has been initiated.')
      await load_project_file_list()
      await router.push({ name: 'project', params: { project_name: project_name } })
    })
    .catch((error) => {
      toast.error('Error starting background job for puzzle data creation:', error.message)
    })
}
const delete_puzzledata = async () => {
  await axios
    .delete(`/projects/project/${project_name}/puzzledata`)
    .then(async () => {
      await load_project_file_list()
    })
    .catch((error) => {
      toast.error('Error deleting puzzle data:', error.message)
    })
}
const create_manuscript = async () => {
  await axios
    .post(`/projects/project/${project_name}/manuscript/`, null, {
      params: { print_debug: print_debug.value },
    })
    .then(async () => {
      toast.success('Background job for manuscript creation has been initiated.')
      await load_project_file_list()
      await router.push({ name: 'project', params: { project_name: project_name } })
    })
    .catch((error) => {
      toast.error('Error starting background job for manuscript creation:', error.message)
    })
}
const delete_manuscript = async () => {
  await axios
    .delete(`/projects/project/${project_name}/manuscript/`)
    .then(async () => {
      await load_project_file_list()
      await router.push({ name: 'project', params: { project_name: project_name } })
    })
    .catch((error) => {
      toast.error('Error deleting manuscript:', error.message)
    })
}
const view_manuscript = () => {
  // router.push({
  //   name: 'view-manuscript',
  //   params: { project_name: project_name },
  // })
  const pdfSource: string =
    'http://'+import.meta.env.VITE_API_BASE_URL +
    '/projects/project/' +
    project_name +
    '/manuscript/manuscript.pdf'
  window.open(pdfSource, '_blank')
}
</script>

<template>
  <div class="card">
    <HeadingBlock :level="1">{{ project_name }}</HeadingBlock>
    <DividerLine />
    <ProjectFile
      hero_file_title="Project Settings"
      :hero_file_name="hero_files.project_settings"
      :named_file_state="named_file_state(hero_files.project_settings)"
      :allowed_actions="['edit', 'create']"
      @edit="edit_project_settings"
      @create="edit_project_settings"
    />
    <ProjectFile
      hero_file_title="Wordlist"
      :hero_file_name="hero_files.wordlist"
      :named_file_state="named_file_state(hero_files.wordlist)"
      :allowed_actions="[
        'edit',
        'delete',
        named_file_state(hero_files.project_settings)[0] === 'exists' ? 'create' : '',
      ]"
      @edit="edit_wordlist"
      @delete="delete_wordlist"
      @create="create_wordlist"
    />
    <ProjectFile
      hero_file_title="Puzzle Data"
      :hero_file_name="hero_files.puzzledata"
      :named_file_state="named_file_state(hero_files.puzzledata)"
      :allowed_actions="[
        'edit',
        'delete',
        named_file_state(hero_files.project_settings)[0] === 'exists' &&
        named_file_state(hero_files.wordlist)[0] === 'exists'
          ? 'create'
          : '',
      ]"
      @edit="edit_puzzledata"
      @delete="delete_puzzledata"
      @create="create_puzzledata"
    />
    <ProjectFile
      hero_file_title="Manuscript"
      :hero_file_name="hero_files.manuscript"
      :named_file_state="named_file_state(hero_files.manuscript)"
      :allowed_actions="[
        'edit',
        'delete',
        named_file_state(hero_files.project_settings)[0] === 'exists' &&
        named_file_state(hero_files.puzzledata)[0] === 'exists'
          ? 'create'
          : '',
      ]"
      @edit="view_manuscript"
      @delete="delete_manuscript"
      @create="create_manuscript"
    />
    <div class="print_debug">
      <InputBlock type="bool" v-model="print_debug">Print Debug:</InputBlock>
    </div>
    <HeadingBlock :level="3">Other Files</HeadingBlock>
    <div class="project_files">
      <template v-for="(file, index) in file_list?.project_files" :key="index">
        <div class="project_file" v-if="file_in_hero_list(file.name)">
          {{ file.name }}
        </div>
      </template>
    </div>
  </div>
  <RouterView @saved="load_project_file_list" />
</template>

<style scoped>
.print_debug {
  display: flex;
  justify-content: flex-end;
}
</style>
