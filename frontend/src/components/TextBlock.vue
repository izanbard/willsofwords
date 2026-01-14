<script lang="ts" setup></script>

<template>
  <p>
    <slot></slot>
  </p>
</template>

<style scoped>
p {
  &:not(:last-child) {
    margin-bottom: 16px;
  }
}
</style>
