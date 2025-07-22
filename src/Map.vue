<script setup>
import { ref, onMounted } from 'vue'
import { OlaMaps } from 'olamaps-web-sdk'


const lat = ref(null);
const lng = ref(null);
const myMap = ref(null)
const coord=[78.83860388611959,23.05195757298101]
const showPopup = ref(false);
const popupCoords = ref({ x: 0, y: 0 });
const popupData = ref({ title: '', lat: null, lng: null });


onMounted(() => {
  const Maps = new OlaMaps({
    apiKey: "JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy",
  })
const el = document.createElement('div');
el.className = 'custom-marker';
el.innerHTML = `<div class="marker-label">📍 Jaipur Parking</div>`;

// Optional: Add a click handler
el.addEventListener('click', (e) => {
  const bounds = document.getElementById('ola-map').getBoundingClientRect();

  popupCoords.value = {
    x: e.clientX - bounds.left,
    y: e.clientY - bounds.top,
  };

  popupData.value = {
    title: '📍 Jaipur Parking',
    lat: 26.88426881385905,
    lng: 75.71019784099505, 
  };

  showPopup.value = true;
});


  const map = Maps.init({
      container: 'ola-map',
      style: "https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json",
      center: [78.9629, 22.5937], 
    zoom: 3.5,
    });

  const defaultMarker = Maps.addMarker({
  element:el,
  offset: [0, 0],
  anchor: 'bottom', 
})
.setLngLat([75.71019784099505,26.88426881385905])
.addTo(map);


  let marker;

  map.on('click', (e) => {
    lat.value = e.lngLat.lat;
    lng.value = e.lngLat.lng;

    if (marker) {
      marker.setLngLat([lng.value, lat.value]);
    } else {
      marker = new window.OlaMaps.Marker()
        .setLngLat([lng.value, lat.value])
        .addTo(map);
    }
  });
});
</script>

<template>
  <div>
    <div id="ola-map" class="map-container"></div>
    <div class="coords">
      <p v-if="lat && lng">📍 Lat: {{ lat }}, Lng: {{ lng }}</p>
    </div>
  </div>
  <div
  v-if="showPopup"
  class="popup-box"
  :style="{ top: popupCoords.y + 'px', left: popupCoords.x + 'px' }"
>
  <h3>{{ popupData.title }}</h3>
  <p>Lat: {{ popupData.lat }}</p>
  <p>Lng: {{ popupData.lng }}</p>
  <button @click="showPopup = false">Close</button>
</div>
</template>

<style scoped>
.map-container {
  height: 90vh;
  width: 100%;
}
.coords {
  padding: 1rem;
  font-size: 1rem;
}
.custom-marker {
  cursor: pointer;
}

.marker-label {
  background: #fff;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  white-space: nowrap;
}
.popup-box {
  position: absolute;
  background: white;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  z-index: 10;
}

</style>
