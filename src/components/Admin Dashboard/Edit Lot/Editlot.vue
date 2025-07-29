<template>
  <Loading v-if="loading" />
  <div v-else class="edit-lot-wrapper">
    <h2>Edit Parking Lots</h2>

    <div v-if="error" class="error">{{ error }}</div>
    <table class="summary-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Total Spots</th>
          <th>Price/Hour</th>
          <th>Location</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in lots" :key="lot.id" @click="selectLot(lot)" class="clickable-row">
          <td>{{ lot.name }}</td>
          <td>{{ lot.total_spots }}</td>
          <td>{{ lot.price_per_hour }}</td>
          <td>{{ lot.address_line1 }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Edit Form -->
    <div v-if="selectedLot" class="edit-section">
      <h3>Edit Lot: {{ selectedLot.name }}</h3>
      <form @submit.prevent="saveLot">
        <label>Name:
          <input v-model="form.name" required />
        </label>

        <label>Address Line 1:
          <input v-model="form.addressLine1" @change="fetchCoordsFromAddress" />
        </label>

        <label>Address Line 2:
          <input v-model="form.addressLine2" @change="fetchCoordsFromAddress" />
        </label>

        <label>Latitude:
          <input v-model="form.latitude" readonly />
        </label>

        <label>Longitude:
          <input v-model="form.longitude" readonly />
        </label>

        <label>Total Spots:
          <input v-model.number="form.totalSpots" type="number" />
        </label>

        <label>Price Per Hour:
          <input v-model.number="form.pricePerHour" type="number" step="0.01" />
        </label>

        <div class="form-buttons">
          <button type="submit">💾 Save</button>
          <button type="button" @click="deleteLot">🗑 Delete</button>
        </div>
      </form>

      <div id="map" class="map"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { OlaMaps } from 'olamaps-web-sdk'
import { authFetch } from '../../../utils/authFetch.js'
import Loading from '../../../utils/Loading.vue'


const lots = ref([])
const selectedLot = ref(null)
const form = ref({})
const map = ref(null)
const marker = ref(null)
const ola = ref(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await authFetch('http://localhost:5000/parkinglots')
    lots.value = await res.json()
  } catch (err) {
    error.value = 'Error fetching lots'
  }
  finally {
    loading.value = false
  }
})

function selectLot(lot) {
  selectedLot.value = lot
  form.value = {
    id: lot.id,
    name: lot.name,
    totalSpots: lot.total_spots,
    pricePerHour: lot.price_per_hour,
    addressLine1: lot.address_line1,
    addressLine2: lot.address_line2,
    latitude: lot.latitude,
    longitude: lot.longitude,
  }

  setTimeout(() => initMap(), 0)
}

function initMap() {
  if (!ola.value) {
    ola.value = new OlaMaps({
      apiKey: 'JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy',
    })
  }

  map.value = ola.value.init({
    container: 'map',
    center: [form.value.longitude, form.value.latitude],
    zoom: 15,
  })

  marker.value = ola.value.addMarker()
    .setLngLat([form.value.longitude, form.value.latitude])
    .addTo(map.value)

  map.value.on('click', async (e) => {
    const lng = e.lngLat.lng
    const lat = e.lngLat.lat
    form.value.latitude = lat.toFixed(6)
    form.value.longitude = lng.toFixed(6)
    marker.value.setLngLat([lng, lat])
    await fetchAddressFromCoords(lat, lng)
  })
}

async function fetchCoordsFromAddress() {
  const query = encodeURIComponent(`${form.value.addressLine1} ${form.value.addressLine2}`.trim())
  try {
    const res = await fetch(`https://api.olamaps.io/places/v1/geocode?address=${query}&api_key=JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy`)
    const data = await res.json()
    const loc = data?.results?.[0]?.geometry?.location
    if (loc) {
      form.value.latitude = loc.lat.toFixed(6)
      form.value.longitude = loc.lng.toFixed(6)
      if (marker.value) marker.value.setLngLat([loc.lng, loc.lat])
      if (map.value) map.value.flyTo({ center: [loc.lng, loc.lat], zoom: 15 })
    }
  } catch (err) {
    console.error('Geocoding failed', err)
  }
}

async function fetchAddressFromCoords(lat, lng) {
  try {
    const res = await fetch(`https://api.olamaps.io/places/v1/reverse-geocode?latlng=${lat},${lng}&api_key=JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy`)
    const data = await res.json()
    const result = data?.results?.[0]?.formatted_address
    if (result) {
      const parts = result.split(', ')
      form.value.addressLine1 = parts[0] || ''
      form.value.addressLine2 = parts.slice(1).join(', ') || ''
    }
  } catch (err) {
    console.error('Reverse geocoding failed', err)
  }
}

async function saveLot() {
  try {
    const res = await fetch('http://localhost:5000/editlot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const data = await res.json()
    alert(data.message || 'Updated successfully')
  } catch (err) {
    console.error('Save failed', err)
  }
}

async function deleteLot() {
  if (!confirm('Are you sure?')) return
  try {
    const res = await fetch(`http://localhost:5000/deletelot/${form.value.id}`, {
      method: 'POST',
    })
    const data = await res.json()
    alert(data.message || 'Deleted successfully')
    lots.value = lots.value.filter(l => l.id !== form.value.id)
    selectedLot.value = null
  } catch (err) {
    console.error('Delete failed', err)
  }
}
</script>

<style scoped>
.edit-lot-wrapper {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-table {
  width: 100%;
  border-collapse: collapse;
  cursor: pointer;
}

.summary-table th, .summary-table td {
  border: 1px solid #ccc;
  padding: 10px;
}

.clickable-row:hover {
  background-color: #f0f0f0;
}

.edit-section {
  margin-top: 20px;
  display: flex;
  gap: 20px;
}

form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

#map {
  flex: 2;
  height: 400px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>
