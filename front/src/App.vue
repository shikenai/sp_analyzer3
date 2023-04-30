<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div id="wrapper">
    wrapper
    <nav id="header">

    </nav>
    <div id="main">
      <a href="api/index">wei</a>
    </div>
  </div>
</template>

<style scoped>
#wrapper {
  min-height: 800px;
  display: grid;
  grid-template:
        "header  header header" 60px
        "main    main   main  " 1fr
        /150px   1fr;
  gap: 5px;
}

#header {
  grid-area: header;
  border: 1px solid black;
  padding: 20px;
}

#left {
  grid-area: left;
  border: 1px solid black;
  text-align: center;
}

#main {
  grid-area: main;
  border: 1px solid black;
}


</style>
