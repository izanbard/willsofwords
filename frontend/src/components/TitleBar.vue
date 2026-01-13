<script setup lang="ts">

</script>

<template>
  <div id="header" class="card">
    <img alt="Logo" class="header_image" src="/images/logo.png"/>
    <h1>Wordsworth Puzzle Creator</h1>
  </div>
</template>

<style scoped>
#header {
  min-height: 220px;
  max-height: 220px;
  line-height: 1;
  display: grid;
  grid-template-columns: 200px auto;
  align-items: center;
}

.header_image {
  margin: 0;
  width: 180px;
  height: 180px;
}

h1 {
  font-family: 'Verdana Bold', Inter, sans-serif;
  font-variant-caps: small-caps;
  font-synthesis-weight: auto;
  font-weight: bolder;
  font-size: 3.5em;
  letter-spacing: 0.03em;
  justify-self: center;
  width: fit-content;
  text-align: center;
}
</style>
