<script lang="ts" setup>
defineProps<{
  type: 'info' | 'warning' | 'critical'
}>()
const icon_lookup = {
  info: 'info',
  warning: 'warning',
  critical: 'error',
}
</script>
<template>
  <div class="callout" :class="type">
    <div class="callout_icon">
      <span class="material-symbols-outlined sized">{{ icon_lookup[type] }}</span>
      <div>{{ type }}</div>
    </div>
    <div class="callout_text">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.callout {
  display: grid;
  grid-template-columns: 50px auto;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
}
.callout_icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  border-right: 1px solid var(--vt-c-divider-light-1);
  padding: 0.5rem;
}
.callout_text {
  align-self: center;
  padding-left: 0.5rem;
}
.info {
  border: 1px solid var(--vt-c-green);
  background-color: var(--vt-c-green-trans-bkg);
}
.warning {
  border: 1px solid var(--vt-c-orange);
  background-color: var(--vt-c-orange-trans-bkg);
}
.critical {
  border: 1px solid var(--vt-c-red);
  background-color: var(--vt-c-red-trans-bkg);
}
</style>
