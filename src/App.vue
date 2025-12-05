<template>
  <div id="app">
    <DetectionView />
  </div>
</template>

<script>
import DetectionView from './components/DetectionView.vue'

export default {
  name: 'App',
  components: {
    DetectionView,
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
