<template>
  <Loading v-if="loading" />  
  <div class="container Parking">

    <div v-if="error" class="error">{{ error }}</div>

    <div class="table-wrapper" v-if="!loading && lots.length">
      <table class="parking-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Total Spots</th>
            <th>Price/Hour</th>
            <th>Address Line 1</th>
            <th>Address Line 2</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(lot, index) in lots" :key="index">
            <td>{{ lot.name }}</td>
            <td>{{ lot.total_spots }}</td>
            <td>{{ lot.price_per_hour }}</td>
            <td>{{ lot.address_line1 }}</td>
            <td>{{ lot.address_line2 }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Map of lots -->
    <div class="map-wrapper" v-if="!loading && lots.length">
      <Map :lots="mappedLots" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Map from './Map.vue'
import Loading from '../../../utils/Loading.vue'
import { authFetch } from '../../../utils/authFetch.js'

const lots = ref([])
const loading = ref(true)
const error = ref('')

const mappedLots = computed(() =>
  lots.value.map(({ latitude, longitude, name }) => ({
    latitude,
    longitude,
    name
  }))
)

onMounted(async () => {
  try {
    const response = await authFetch('http://localhost:5000/parkinglots')
    if (!response.ok) throw new Error('Expired Token')
    lots.value = await response.json()
  } catch (err) {
    error.value = err.message || 'An error occurred'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.container {
  display: flex;
  gap: 20px;
  padding: 20px;
  box-sizing: border-box;
}

.table-wrapper {
  flex: 1;
  max-width: 35%;
  overflow-y: auto;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  border: 1px solid #ccc;
}

.parking-table {
  width: 100%;
  border-collapse: collapse;
}

.parking-table th,
.parking-table td {
  border: 1px solid #ccc;
  padding: 10px;
  text-align: left;
}

.map-wrapper {
  flex: 2;
  height: 100%;
  min-width: 0;
}

.status {
  text-align: center;
  font-style: italic;
}

.error {
  color: red;
  text-align: center;
  margin-bottom: 10px;
}
</style>
