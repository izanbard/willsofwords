<script setup lang="ts">
const { solution = false, directions, profane=false } = defineProps<{
  solution?: boolean
  directions?: { NS: boolean; EW: boolean; NESW: boolean; NWSE: boolean }
  profane?:boolean
  profane_answer?:boolean
}>()
const emit = defineEmits(['pressed'])
const ping_event = () => {
  if (!solution) {
    emit('pressed')
  }
}
</script>

<template>
  <div class="grid_square" @click="ping_event" :class="{ is_profane: profane, is_both: profane_answer }">
    <slot></slot>
    <template v-if="directions && solution">
      <div class="NS" v-if="directions.NS"></div>
      <div class="EW" v-if="directions.EW"></div>
      <div class="NESW" v-if="directions.NESW"></div>
      <div class="NWSE" v-if="directions.NWSE"></div>
    </template>
  </div>
</template>

<style scoped>

.grid_square {
  border: 1px solid var(--color-border);
  padding: 0.15em;
  text-align: center;
  cursor: pointer;
  position: relative;
}
.NS::after {
  content: '';
  border-left: 2px solid var(--vt-c-black);
  height: 1.45em;
  position: absolute;
  left: 50%;
  top: -0.1em;
}
.EW::after {
  content: '';
  border-top: 2px solid var(--vt-c-black);
  width: 1.35em;
  position: absolute;
  left: -0.1em;
  top: 50%;
}
.NESW::after {
  content: '';
  position: absolute;
  top: 100%;
  left: -0.1em;
  width: 1.93em;
  height: 0;
  border-top: 2px solid var(--vt-c-black);
  transform: rotate(-47.5deg);
  transform-origin: left top;
}
.NWSE::after {
  content: '';
  position: absolute;
  top: -0.1em;
  left: 0;
  width: 1.93em;
  height: 0;
  border-bottom: 2px solid var(--vt-c-black);
  transform: rotate(47.5deg);
  transform-origin: left top;
}
.is_profane {
  background-color: var(--vt-c-red-light);
}
.is_both {
  background-color: var(--vt-c-orange-trans-bkg);
}
</style>
