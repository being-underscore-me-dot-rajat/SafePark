<template>
<Loading v-if="loading" />
  <div v-else class="booking-table">
    <h2>All Bookings</h2>
    <table>
      <thead>
        <tr>
          <th>User ID</th>
          <th>User Name</th>
          <th>Lot</th>
          <th>Spot</th>
          <th>Start Time</th>
          <th>End Time</th>
          <th>Duration</th>
          <th>Cost</th>
          <th>Delete</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="booking in bookings" :key="booking.Bid">
          <td>{{ booking.user_id }}</td>
          <td>{{ booking.user_name }}</td>
          <td>{{ booking.lot }}</td>
          <td>{{ booking.spot }}</td>
          <td> {{formatDateTime( booking.starttime )}}</td>
          <td>{{formatDateTime( booking.endtime )}}</td>
          <td>
                <div v-if="booking.endtime">{{ calculateDurationHours(booking.starttime, booking.endtime) }} hrs</div>
                <span class="cost-unavailable" v-else>Ongoing</span>
            </td>
          <td>
          <template v-if="booking.endtime">
                ₹{{ booking.cost  }}
              </template>
              <template v-else>
                <span class="cost-unavailable">Pending</span>
              </template></td>
          <td>
            <button class="delete-btn" @click="deleteBooking(booking.Bid)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="message">{{ message }}</p>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue';
import { authFetch } from '../../../Utils/authFetch.js';
import Loading from '../../../utils/Loading.vue'

export default {
  components: {
    Loading
  },
  data() {
    return {
      bookings: [],
      message: '',
      loading:true
    };
  },
  mounted() {
    this.fetchBookings();
  },
  methods: {
    async fetchBookings() {
      try {
        const res = await authFetch('http://localhost:5000/getallbookings');
        this.bookings = await res.json();
      } catch (err) {
        console.error('Failed to fetch bookings', err);
      }
      finally {
    this.loading = false;
  }
    },
    async deleteBooking(bookingId) {
      const confirmed = window.confirm('Are you sure you want to delete this booking?');
      if (!confirmed) return;

      try {
        const res = await authFetch(`http://localhost:5000/deletebooking/${bookingId}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        this.message = data.message || 'Booking deleted.';
        // Refresh booking list
        this.bookings = this.bookings.filter(b => b.Bid !== bookingId);
      } catch (err) {
        console.error('Failed to delete booking', err);
        this.message = 'Failed to delete booking.';
      }
    },
    calculateDurationHours(start, end) {
  const startTime = new Date(start);
  const endTime = new Date(end);
  const durationMs = endTime - startTime;
  const durationHours = durationMs / (1000 * 60 * 60);
  return durationHours.toFixed(2); 
},
  
formatDateTime(timestamp){
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
  }
};
</script>


<style scoped>
.all-bookings {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th,
td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

th {
  background: #f5f5f5;
}

.pending {
  color: #f39c12;
  font-weight: bold;
}

.booking-table table {
  width: 100%;
  border-collapse: collapse;
}
.booking-table th, .booking-table td {
  padding: 8px;
  border: 1px solid #ccc;
  text-align: center;
}
.delete-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 18px;
}
.delete-btn:hover {
  color: red;
}

.cost-unavailable {
  color: #f39c12;
  font-weight: bold;
}

</style>
