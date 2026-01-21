<script setup lang="ts">
import ButtonBox from '@/components/ButtonBox.vue'
import HeadingBlock from '@/components/HeadingBlock.vue'

defineEmits(['edit', 'delete', 'create'])
defineProps<{
  hero_file_title: string
  hero_file_name: string
  named_file_state: (number | string)[]
  allowed_actions: string[]
}>()
</script>

<template>
  <HeadingBlock :level="3">{{ hero_file_title }}</HeadingBlock>
  <template v-if="named_file_state[0] === 'creating'">
    <div class="progress_main">
      <div class="creating">Creating {{ hero_file_name }}... {{ named_file_state[1] }}%</div>
    </div>
  </template>
  <div v-else class="project_file">
    <div class="file" :class="named_file_state[0]">
      <em>{{ hero_file_name }}</em>
    </div>
    <template v-if="named_file_state[0] === 'exists'">
      <div class="actions">
        <ButtonBox
          v-if="allowed_actions.includes('edit')"
          icon="edit"
          text="View/Edit"
          colour="blue"
          @pressed="$emit('edit', hero_file_name)"
        />
        <ButtonBox
          v-if="allowed_actions.includes('delete')"
          icon="delete"
          text="Delete"
          colour="red"
          @pressed="$emit('delete', hero_file_name)"
        />
      </div>
    </template>
    <template v-if="named_file_state[0] === 'not_exists'">
      <ButtonBox
        v-if="allowed_actions.includes('create')"
        icon="add"
        text="Create"
        colour="green"
        @pressed="$emit('create', hero_file_name)"
      />
    </template>
  </div>
</template>

<style scoped>
.project_file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.file {
  padding: 0.5rem;
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}
.exists {
  background-color: var(--vt-c-green-trans-bkg);
}
.not_exists {
  background-color: var(--vt-c-red-trans-bkg);
}
.progress_main {
  border: 1px solid var(--color-border);
  background-color: var(--vt-c-yellow-trans-bkg);
  border-radius: 0.5rem;
}
.creating {
  background-color: var(--vt-c-green-trans-bkg);
  width: v-bind(named_file_state[1] + '%');
  overflow: visible;
  white-space: nowrap;
  padding: 0.5rem;
  border-radius: 0.5rem 0 0 0.5rem;
}
</style>
