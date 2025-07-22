<template>
  <div class="loading-container">
    <video
      class="loading-video"
      autoplay
      muted
      loop
      playsinline
    >
      <source src="/Loading Video.mp4" type="video/mp4" />
    </video>
  </div>
</template>

<script setup>
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.loading-video {
  width: 150px;
  height: auto;
  border-radius: 12px;
  margin-bottom: 15px;
}
</style>
