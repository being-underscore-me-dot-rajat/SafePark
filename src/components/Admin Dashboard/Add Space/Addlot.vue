<template>
  <div class="add-lot-container">
    <div class="form-section">
      <h2>Add New Parking Lot</h2>

      <form @submit.prevent="handleSubmit">
        <label>
          Lot Name:
          <input v-model="form.name" required />
        </label>

        <label>
          Address Line 1:
          <input v-model="form.addressLine1" placeholder="e.g., Crown Plaza" />
        </label>

        <label>
          Address Line 2:
          <input v-model="form.addressLine2" placeholder="e.g., Jaipur, Rajasthan" />
        </label>

        <button type="button" @click="fetchCoordsFromAddress">Get Coordinates</button>

        <label>
          Latitude:
          <input v-model="form.latitude" readonly />
        </label>

        <label>
          Longitude:
          <input v-model="form.longitude" readonly />
        </label>

        <label>
          Number of Spots:
          <input v-model.number="form.totalSpots" type="number" min="0" />
        </label>

        <label>
          Price Per Hour (₹):
          <input v-model.number="form.pricePerHour" type="number" step="0.01" min="0" />
        </label>

        <button type="submit">Save Lot</button>
      </form>

      <p v-if="status" class="status-msg">{{ status }}</p>
    </div>

    <div class="map-section">
      <div id="ola-map" class="map-container"></div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import { OlaMaps } from 'olamaps-web-sdk'

const olaMaps = ref(null)
const map = ref(null)
const marker = ref(null)

const form = ref({
  name: '',
  addressLine1: '',
  addressLine2: '',
  latitude: '',
  longitude: '',
  totalSpots: 0,
  pricePerHour: 0,
})

const status = ref('')

onMounted(() => {
  olaMaps.value = new OlaMaps({
    apiKey: 'JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy',
  })

  map.value = olaMaps.value.init({
    container: 'ola-map',
    style: 'https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json',
    center: [78.9629, 22.5937],
    zoom: 4,
  })

  map.value.on('click', async (e) => {
    const lng = e.lngLat.lng
    const lat = e.lngLat.lat

    form.value.latitude = lat.toFixed(6)
    form.value.longitude = lng.toFixed(6)

    if (!marker.value) {
      marker.value = olaMaps.value
        .addMarker()
        .setLngLat([lng, lat])
        .addTo(map.value)
    } else {
      marker.value.setLngLat([lng, lat])
    }

    await fetchAddressFromCoords(lat, lng)
  })
})

async function fetchAddressFromCoords(lat, lng) {
  try {
    const res = await fetch(`https://api.olamaps.io/places/v1/reverse-geocode?latlng=${lat},${lng}&api_key=JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy`)
    const data = await res.json()
    console.log(data)

    const result = data?.geocodingResults?.[0] || data?.results?.[0]
    if (result?.formatted_address) {
      const addressParts = result.formatted_address.split(', ')
      form.value.addressLine1 = addressParts[0] || ''
      form.value.addressLine2 = addressParts.slice(1).join(', ') || ''
      status.value = 'Address auto-filled from map click.'
    } else {
      status.value = 'No address found for location.'
    }
  } catch (err) {
    status.value = 'Reverse geocoding failed.'
    console.error(err)
  }
}

async function fetchCoordsFromAddress() {
  try {
    const addressQuery = encodeURIComponent(
      `${form.value.addressLine1} ${form.value.addressLine2}`.trim()
    )

    const res = await fetch(
      `https://api.olamaps.io/places/v1/geocode?address=${addressQuery}&api_key=JrfosptCCKRHaDu9mMXXESTPNiNF7r4aObU8R3Gy`
    )

    const data = await res.json()
    console.log(data)

    const result = data?.results?.[0] || data?.geocodingResults?.[0]
    const location = result?.geometry?.location

    if (location?.lat && location?.lng) {
      form.value.latitude = location.lat.toFixed(6)
      form.value.longitude = location.lng.toFixed(6)

      if (!marker.value) {
        marker.value = olaMaps.value
          .addMarker()
          .setLngLat([location.lng, location.lat])
          .addTo(map.value)
      } else {
        marker.value.setLngLat([location.lng, location.lat])
      }

      map.value.flyTo({ center: [location.lng, location.lat], zoom: 15 })
      status.value = 'Coordinates fetched from address.'
    } else {
      status.value = 'Could not find coordinates for the address.'
    }
  } catch (err) {
    status.value = 'Geocoding failed.'
    console.error(err)
  }
}

async function handleSubmit() {
  console.log('Saving lot data:', form.value)
  // You can POST `form.value` to your backend here
  try {
    const response = await fetch('http://localhost:5000/addparkinglots', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form.value),
    })

    const data = await response.json()

    if (response.ok) {
      status.value = data.message || 'Parking lot added successfully.'
      // Optionally reset form:
      form.value = {
        name: '',
        addressLine1: '',
        addressLine2: '',
        latitude: '',
        longitude: '',
        totalSpots: 0,
        pricePerHour: 0,
      }
    } else {
      status.value = data.error || 'Error adding lot.'
    }
  } catch (error) {
    console.error('❌ API error:', error)
    status.value = 'Failed to add lot. Please try again later.'
  }
}
</script>


<style scoped>
.add-lot-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  height: 90vh;
  box-sizing: border-box;
}

.form-section {
  flex: 1;
  max-width: 35%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

form input {
  padding: 6px;
  font-size: 14px;
}

button {
  padding: 6px 12px;
  font-weight: bold;
  cursor: pointer;
}

.map-section {
  flex: 2;
}

.map-container {
  height: 100%;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.status-msg {
  font-size: 0.9rem;
  color: #007bff;
  margin-top: 10px;
}
</style>
export default { ... }
