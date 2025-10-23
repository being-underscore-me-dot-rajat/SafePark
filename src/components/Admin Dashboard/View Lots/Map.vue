<script setup>
import { onMounted, watch, ref } from 'vue'
import { OlaMaps } from 'olamaps-web-sdk'

const props = defineProps({
  lots: {
    type: Array,
    default: () => []
  }
})

const map = ref(null)
const olaMaps = ref(null)

onMounted(() => {
  // console.log('Initializing OlaMaps...')

  olaMaps.value = new OlaMaps({
    apiKey: 'Bring_your_own_😒',
  })

  map.value = olaMaps.value.init({
    container: 'map',
    style: 'https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json',
    center: [78.9629, 22.5937], 
    zoom: 3.5,
  })

  if (props.lots.length) {
    addMarkers(props.lots)
  }
})

watch(
  () => props.lots,
  (newLots) => {
    // console.log('Lots updated:', newLots)
    if (map.value && newLots.length) {
      addMarkers(newLots)
    }
  },
  { immediate: true }
)

function addMarkers(lots) {
  lots.forEach((lot, index) => {
    // console.log(`Adding marker for lot: ${lot.name}`, lot)

    const popup = olaMaps.value
      .addPopup({
        offset: [0, -20],
        anchor: 'bottom',
      })
      .setHTML(`
        <div style="font-size: 14px;">
          <strong>${lot.name}</strong><br/>
        </div>
      `)

    olaMaps.value
      .addMarker()
      .setLngLat([lot.longitude, lot.latitude])
      .setPopup(popup)
      .addTo(map.value)
  })
}
</script>

<template>
  <div>
    <div id="map" class="map-container"></div>
  </div>
</template>

<style scoped>
.map-container {
  height: 70vh;
  width: 90%;
}
</style>
