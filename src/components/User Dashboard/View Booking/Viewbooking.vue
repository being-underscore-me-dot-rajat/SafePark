<template>
  <div class="view-bookings">
    <Loading v-if="loading" />
    <div v-else>
      <h2>Your Bookings</h2>
      <div class="table-container" v-if="bookings.length">
      <table >
        <thead>
          <tr>
            <th>Lot</th>
            <th>Spot</th>
            <th>Price per hour</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Duration</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in [...bookings].reverse()" :key="booking.id">
            <td>
              <a href="#" @click.prevent="redirectToMap(booking.lot_name)">
                {{ booking.lot_name }} 📍
              </a>
            </td>
            <td>{{ booking.spot_number }}</td>
            <td>{{ booking.price_per_hour }}</td>
            <td>{{ formatDateTime(booking.start_time) }}</td>
            <td>
                <button v-if="!booking.end_time" @click="openEndTimeModal(booking)">Provide End Time</button>
                <div v-else>{{  formatDateTime(booking.end_time) }}</div>
            </td>
            <td>
                <div v-if="booking.end_time">{{ calculateDurationHours(booking.start_time, booking.end_time) }} hrs</div>
                <span class="cost-unavailable" v-else>Ongoing</span>
            </td>

            <td>
              <template v-if="booking.end_time">
                ₹{{ booking.cost  }}
              </template>
              <template v-else>
                <span class="cost-unavailable">Pending</span>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
      <p v-else>No bookings found.</p>
      <div v-if="showModal" class="modal">
        <div class="modal-content">
            <h3>Provide End Time for Spot {{ selectedBooking.spot_number }}</h3>
            <input type="datetime-local" v-model="endTimeInput" />
            <div class="modal-actions">
            <button @click="submitEndTime">Submit</button>
            <button @click="closeModal">Cancel</button>
            </div>
            <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </div>
    </div>

      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authFetch } from '../../../utils/authFetch.js'
import Loading from '../../../utils/Loading.vue'
import router from '../../../router'

const bookings = ref([])
const loading = ref(true)

function toISTISOString(localDateTime) {
  const date = new Date(localDateTime);

  const utcTime = date.getTime() + (date.getTimezoneOffset() * 60 * 1000);
  const istOffsetMs = 5.5 * 60 * 60 * 1000;
  const istDate = new Date(utcTime + istOffsetMs);

  const year = istDate.getFullYear();
  const month = String(istDate.getMonth() + 1).padStart(2, '0');
  const day = String(istDate.getDate()).padStart(2, '0');
  const hours = String(istDate.getHours()).padStart(2, '0');
  const minutes = String(istDate.getMinutes()).padStart(2, '0');

  
  return `${year}-${month}-${day}T${hours}:${minutes}+05:30`;
}

const calculateDurationHours = (start, end) => {
  const startTime = new Date(start);
  const endTime = new Date(end);
  const durationMs = endTime - startTime;
  const durationHours = durationMs / (1000 * 60 * 60);
  return durationHours.toFixed(2); 
}


const fetchBookings = async () => {
  try {
    const res = await authFetch('http://localhost:5000/viewbookings')
    const data = await res.json()
    bookings.value = data
  } catch (err) {
    console.error('Error fetching bookings:', err)
  } finally {
    loading.value = false
  }
}

const redirectToMap = async (lot_name) => {
  try {
    const res = await authFetch(`http://localhost:5000/getlotcoords/${lot_name}`)
    const data = await res.json()
    const lat = data.latitude
    const lng = data.longitude
    window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, '_blank')
  } catch (err) {
    console.error("Failed to get lot location:", err)
  }
}

const formatDateTime = (timestamp) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  } catch {
    return "Invalid"
  }
}

const showModal = ref(false)
const selectedBooking = ref(null)
const endTimeInput = ref(null)
const errorMessage = ref("")

const openEndTimeModal = (booking) => {
  selectedBooking.value = booking
  endTimeInput.value = toISTISOString(new Date()).slice(0, 16)
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedBooking.value = null
  endTimeInput.value = null
  errorMessage.value = ""
}


const submitEndTime = async () => {
  if (!selectedBooking.value || !endTimeInput.value) return;

  const endTime = new Date(endTimeInput.value);
  const now = new Date();
  const startTime = new Date(selectedBooking.value.start_time);

  if (endTime <= startTime) {
    errorMessage.value = "End time must be after start time.";
    return;
  }

  try {
    const formattedEndTime = toISTISOString(endTime)

    const res = await authFetch(`http://localhost:5000/provideendtime`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        booking_id: selectedBooking.value.id,
        end_time: formattedEndTime // <- Consistent with Make Booking
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong");

    await fetchBookings();
    closeModal();
  } catch (err) {
    errorMessage.value = err.message;
  }
};


onMounted(() => {
  fetchBookings()
})
</script>

<style scoped>

.modal {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
}

.modal-actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-around;
}

.error {
  color: red;
  margin-top: 8px;
}

.view-bookings {
  padding: 20px;
}
table {
  width: 100%;
  border-collapse:none;
}
th, td {
  padding: 12px;
  border: 1px solid #ccc;
  text-align: left;
}
a {
  color: #5e17eb;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
button {
  margin-right: 8px;
  padding: 6px 12px;
  background-color: #5e17eb;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background-color: #4310b4;
}
.cost-unavailable {
  color: #f39c12;
  font-weight: bold;
}

.table-container::-webkit-scrollbar {
  width: 8px;
}
.table-container::-webkit-scrollbar-thumb {
  background-color: #aaa;
  border-radius: 4px;
}
.table-container {
  max-height: 60vh; /* or any height you prefer */
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 6px;
}


</style>
