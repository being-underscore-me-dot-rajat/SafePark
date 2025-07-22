<template>
  <div class="booking-container">
    <h2>Make a Booking</h2>

    <form @submit.prevent="confirmBooking">
      <div class="form-group">
        <label>Parking Lot</label>
        <select v-model="booking.spot_id" required>
          <option disabled value="">Select a parking lot</option>
          <option v-for="lot in lots" :key="lot.id" :value="lot.id">
            {{ lot.name }} ({{ lot.address_line1 }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Start Time</label>
        <input
          type="datetime-local"
          v-model="booking.start_time"
          :min="minDateTime"
          required
          @change="unlockEndTime"
        />
      </div>

      <div class="form-group">
        <label>End Time</label>
        <input
          type="datetime-local"
          v-model="booking.end_time"
          :min="booking.start_time"
          :disabled="!booking.start_time"
        />
      </div>

      <button type="submit">Book Now</button>
    </form>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { authFetch } from '../../../Utils/authFetch.js';

export default {
  props: ['switchTab'], // function from parent to switch active tab
  data() {
    return {
      lots: [],
      booking: {
        user_id: 1, 
        spot_id: '',
        start_time: '',
        end_time: '',
        remarks: ''
      },
      message: '',
      minDateTime: ''
    };
  },
  mounted() {
    this.fetchLots();
    this.setMinDateTime();
  },
  methods: {
    async fetchLots() {
      try {
        const res = await authFetch('http://localhost:5000/parkinglots');
        this.lots = await res.json();
      } catch (err) {
        console.error("Failed to fetch lots", err);
      }
    },
    setMinDateTime() {
      const now = new Date();
      now.setSeconds(0, 0); 
      this.minDateTime = now.toISOString().slice(0, 16);
    },
    unlockEndTime() {
      if (this.booking.start_time) {
        this.booking.end_time = '';
      }
    },
    async confirmBooking() {
      const confirmed = window.confirm("Do you want to confirm this booking?");
      if (!confirmed) return;

      if (new Date(this.booking.start_time) < new Date()) {
        this.message = "Start time cannot be in the past.";
        return;
      }

      if (new Date(this.booking.end_time) <= new Date(this.booking.start_time)) {
        this.message = "End time must be after start time.";
        return;
      }

      await this.submitBooking();
    },
    async submitBooking() {
      const payload = {
        spot_id: this.booking.spot_id,
        start_time: this.booking.start_time,
        end_time: this.booking.end_time,
        cost: this.calculateCost(this.booking.start_time, this.booking.end_time),
        remarks: this.booking.remarks
      };

      try {
        const res = await authFetch('http://localhost:5000/addbooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        this.message = data.message || "Booking successful.";
        window.confirm("Booking successful");
        this.$emit('booking-success'); // 👈 emit event to parent
      } catch (err) {
        console.error("Booking failed", err);
        this.message = "Booking failed. Please try again.";
      }
    },
    calculateCost(start, end) {
      const startTime = new Date(start);
      const endTime = new Date(end);
      const hours = (endTime - startTime) / (1000 * 60 * 60);
      const rate = 50; // Fixed rate
      return Math.ceil(hours * rate);
    }
  }
};
</script>

<style scoped>
.booking-container {
  max-width: 600px;
  margin: 0 auto;
  background: #f5f9ff;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

h2 {
  color: #123c78;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: bold;
  color: #2c3e50;
}

input,
select {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}

button {
  background-color: #4c72e7;
  color: white;
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background-color: #375bc1;
}

.message {
  margin-top: 1rem;
  font-weight: bold;
  color: #2e7d32;
}
</style>
