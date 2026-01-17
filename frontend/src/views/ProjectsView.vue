<script setup lang="ts">
import { onBeforeMount, onBeforeUnmount, onMounted, ref } from 'vue'
import { useToast } from 'vue-toast-notification'
import axios from 'axios'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'
import DividerLine from '@/components/DividerLine.vue'
import ButtonBox from '@/components/ButtonBox.vue'
import CalloutBox from '@/components/CalloutBox.vue'
import InputBlock from '@/components/InputBlock.vue'

let reloader: number | undefined

const project_list = ref<
  Record<
    string,
    {
      name: string
      project_files: Record<string, { name: string; modified_date: string }>
    }
  >
>({})
const loading = ref<boolean>(true)
const delete_confirm = ref<boolean>(false)
const rename_confirm = ref<boolean>(false)
const action_target = ref<string>('')
const new_name = ref<string>('')
const make_a_copy = ref<boolean>(false)
const toast = useToast()

const load_list = async () => {
  await axios
    .get('/projects/')
    .then((response) => {
      project_list.value = response.data.projects
      loading.value = false
    })
    .catch((error) => {
      toast.error('Failed to load project list')
      loading.value = false
    })
}

onBeforeMount(async () => {
  await load_list()
})

onMounted(() => {
  reloader = setInterval(async () => {
    await load_list()
  }, 5000)
})

onBeforeUnmount(() => {
  toast.clear()
  if (reloader) clearInterval(reloader)
})

const date_format = (date: string) => {
  let mydate = new Date(date)
  return mydate.toLocaleTimeString() + ' on ' + mydate.toDateString()
}

const confirm_delete = (project_name: string) => {
  action_target.value = project_name
  delete_confirm.value = true
}

const delete_project = async () => {
  loading.value = true
  delete_confirm.value = false
  await axios
    .delete(`/projects/${action_target.value}`)
    .then(async () => {
      toast.success('Project deleted successfully')
      action_target.value = ''
      await load_list()
    })
    .catch((error) => {
      toast.error('Failed to delete project')
      loading.value = false
    })
}

const confirm_rename = (project_name: string, is_copy: boolean = false) => {
  rename_confirm.value = true
  action_target.value = project_name
  make_a_copy.value = is_copy
}

const copy_project = async () => {
  if (new_name.value.length === 0 || !new_name.value.match(/^[a-zA-Z0-9]+$/)){
    toast.warning('Invalid New Name, letters and numbers only')
    new_name.value = ''
    return
  }
  loading.value = true
  rename_confirm.value = false
  await axios
    .patch('/projects/' + action_target.value + '/' + new_name.value, null, {
      params: { copy: make_a_copy.value },
    })
    .then(async () => {
      toast.success('Project renamed successfully')
      action_target.value = ''
      new_name.value = ''
      await load_list()
    })
    .catch((error) => {
      toast.error('Failed to rename project')
      loading.value = false
    })
}
</script>

<template>
  <div class="card">
    <LoadingSpinner :loading="loading" />
    <HeadingBlock :level="1">List of Projects</HeadingBlock>
    <DividerLine />
    <div class="create">
      <ButtonBox text="New Project" colour="green" @pressed="$router.push({name: 'create-project'})"/>
    </div>
    <div class="project_list">
      <div class="project" v-for="(project, index) in project_list" :key="index">
        <div class="title">
          <HeadingBlock :level="2">{{ project.name }}</HeadingBlock>
          <div class="actions">
            <ButtonBox text="Rename" colour="blue" @pressed="confirm_rename(project.name, false)" />
            <ButtonBox
              text="Duplicate"
              colour="blue"
              @pressed="confirm_rename(project.name, true)"
            />
            <ButtonBox text="Delete" colour="red" @pressed="confirm_delete(project.name)" />
          </div>
        </div>
        <div class="subtitle">
          <HeadingBlock :level="3">Project Files:</HeadingBlock>
        </div>
        <div class="project_files">
          <template v-for="(file, index2) in project.project_files" :key="index2">
            <div class="project_file" v-if="!file.name?.endsWith('.marker')">
              <div class="file">
                <em>{{ file.name }}</em>
              </div>
              <div class="modified">
                <em>
                  <span class="tiny">last modified: </span>{{ date_format(file.modified_date) }}
                </em>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>

  <div class="confirm_container" v-if="delete_confirm">
    <div class="card modal">
      <HeadingBlock :level="2">Are You Sure?</HeadingBlock>
      <div class="actions">
        <ButtonBox text="Proceed" colour="red" @pressed="delete_project()" />
        <ButtonBox text="Cancel" colour="indigo" @pressed="delete_confirm = false" />
      </div>
    </div>
  </div>

  <div class="confirm_container" v-if="rename_confirm">
    <div class="card modal">
      <HeadingBlock :level="2">Proceed with Rename/Duplication?</HeadingBlock>
      <CalloutBox v-if="make_a_copy" type="info">Making a copy</CalloutBox>
      <InputBlock type="text" v-model="action_target" :readonly="true">Old Name: </InputBlock>
      <InputBlock type="text" v-model="new_name">New Name: </InputBlock>
      <div class="actions">
        <ButtonBox text="Proceed" colour="red" @pressed="copy_project()" />
        <ButtonBox text="Cancel" colour="indigo" @pressed="rename_confirm = false" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.create{
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: flex-end;
}
.confirm_container {
  position: fixed;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5);
  width: 100%;
  height: 100%;
}

.modal {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.project {
  border: 1px solid var(--vt-c-divider-dark-1);

  margin-bottom: 0.5rem;
}
.title {
  background-color: var(--vt-c-divider-light-1);
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.subtitle {
  padding-left: 0.5rem;
}
.actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.project_files {
  padding: 0 1rem;
  font-family: Courier, monospace;
}

.project_file {
  margin-bottom: 5px;
  display: flex;
  justify-content: left;
}
.file {
  flex: 1;
  margin-bottom: 0.1rem;
  font-size: 0.8rem;
}
.modified {
  flex: 2;
  margin-bottom: 0.1rem;
  font-size: 0.8rem;
}
.tiny {
  font-size: 0.5rem;
}
</style>
