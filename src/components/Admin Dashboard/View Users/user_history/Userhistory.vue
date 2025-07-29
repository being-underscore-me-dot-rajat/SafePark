<template>
  <div class="user-history">
    <Loading v-if="loading" />
    <div v-else>
      <h2>User Booking History</h2>

      <table v-if="history.length">
        <thead>
          <tr>
            <th>Lot Name</th>
            <th>Spot ID</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(entry, index) in history" :key="index">
            <td>{{ entry.lot }}</td>
            <td>{{ entry.spot }}</td>
            <td>{{ formatDateTime(entry.starttime) }}</td>
            <td>{{ entry.endtime ? formatDateTime(entry.endtime) : "Ongoing" }}</td>
            <td>{{ entry.cost }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>No booking history found for this user.</p>
    </div>
  </div>
</template>


<script setup>
import { ref, watch } from "vue";
import Loading from '../../../../utils/Loading.vue';

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
});

const history = ref([]);
const loading = ref(false);

const fetchUserHistory = async () => {
  if (!props.userId) return;

  loading.value = true;
  try {
    const res = await fetch(`http://localhost:5000/userhistory/${props.userId}`);
    const data = await res.json();
    history.value = data;
  } catch (err) {
    console.error("Error fetching user history:", err);
    history.value = [];
  } finally {
    loading.value = false;
  }
};

watch(() => props.userId, fetchUserHistory, { immediate: true });

const formatDateTime = (datetimeStr) => {
  if (!datetimeStr) return '';
  const d = new Date(datetimeStr);
  return d.toLocaleString();
};
</script>



<style scoped>
.user-history {
  padding: 20px;
}
.input-section {
  margin-bottom: 20px;
}
input {
  margin-left: 10px;
  margin-right: 10px;
  padding: 4px;
}
button {
  padding: 6px 12px;
  background: #4c72e7;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background: #375bc1;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: left;
}
th {
  background: #f5f5f5;
}
</style>
