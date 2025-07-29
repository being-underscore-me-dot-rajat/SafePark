<template>
  <div class="booking-container">
    <h2>Make a Booking</h2>

    <form @submit.prevent="confirmBooking">
      <div class="form-group">
        <label>Parking Lot</label>
        <select v-model="selectedLotId" required>
          <option disabled value="">Select a parking lot</option>
          <option v-for="lot in lots" :key="lot.id" :value="lot.id">
            {{ lot.name }} ({{ lot.address_line1 }}) - Cost per hour: {{ lot.price_per_hour }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Start Time</label>
        <input
          type="datetime-local"
          v-model="rawStartTime"
          :min="minDateTime"
          :step="60"
          required
          @change="updateStartTime"
        />
      </div>

      <div class="form-group">
        <label>End Time</label>
        <input
          type="datetime-local"
          v-model="rawEndTime"
          :min="rawStartTime"
          :step="60"
          :disabled="!rawStartTime"
          @change="updateEndTime"
        />
      </div>

      <button type="submit" :disabled="!selectedLotId || !rawStartTime">Book Now</button>
    </form>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import { authFetch } from '../../../Utils/authFetch.js';

export default {
  data() {
    return {
      lots: [],
      selectedLotId: '',
      rawStartTime: '',
      rawEndTime: '',
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
      this.minDateTime = now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm (no seconds)
    },
    updateStartTime() {
      if (this.rawStartTime) {
        this.booking.start_time = this.toISTISOString(this.rawStartTime);
        this.rawEndTime = '';  // Reset end time if start changes
      }
    },
    updateEndTime() {
      if (this.rawEndTime) {
        this.booking.end_time = this.toISTISOString(this.rawEndTime);
      }
    },
    toISTISOString(localDateTime) {
  // localDateTime is a string from <input type="datetime-local"> (no timezone info)
  // Parse it as local time:
  const date = new Date(localDateTime);

  // Get UTC time in ms:
  const utcTime = date.getTime() + (date.getTimezoneOffset() * 60 * 1000);

  // IST offset in ms
  const istOffsetMs = 5.5 * 60 * 60 * 1000;

  // Create date object in IST:
  const istDate = new Date(utcTime + istOffsetMs);

  // Format as YYYY-MM-DDTHH:mm:ss+05:30
  const year = istDate.getFullYear();
  const month = String(istDate.getMonth() + 1).padStart(2, '0');
  const day = String(istDate.getDate()).padStart(2, '0');
  const hours = String(istDate.getHours()).padStart(2, '0');
  const minutes = String(istDate.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day}T${hours}:${minutes}+05:30`;
},
    async confirmBooking() {
      const startDate = new Date(this.booking.start_time.slice(0, 19));  // Parse without offset for comparison
      const endDate = new Date(this.booking.end_time.slice(0, 19));
      const now = new Date();

      if (startDate < now) {
        this.message = "Start time cannot be in the past.";
        return;
      }
      if (endDate <= startDate) {
        this.message = "End time must be after start time.";
        return;
      }

      await this.submitBooking();
    },
    async submitBooking() {
      const selectedLot = this.lots.find(lot => lot.id === this.selectedLotId);
      if (!selectedLot) {
        this.message = "Lot not found.";
        return;
      }

      const payload = {
        spot_id: this.selectedLotId, 
        start_time: this.booking.start_time,  // IST ISO format
        end_time: this.booking.end_time,      // IST ISO format
        cost: this.calculateCost(this.booking.start_time, this.booking.end_time, selectedLot.price_per_hour),
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
        window.alert("Booking successful");
        this.$emit('booking-success');
      } catch (err) {
        console.error("Booking failed", err);
        this.message = "Booking failed. Please try again.";
      }
    },
    calculateCost(start, end, rate) {
      const startTime = new Date(start.slice(0, 19));  // Parse without offset
      const endTime = new Date(end.slice(0, 19));
      const hours = (endTime - startTime) / (1000 * 60 * 60);
      return Math.ceil(hours) * rate;
    }
  }
};
</script>

