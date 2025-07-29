<template>
  <div class="view-users">
    <Loading v-if="loading" />
    <div v-else>
      <h2>Registered Users</h2>
      <table v-if="users.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>View History</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td class="view-icon" @click="openHistory(user.id)">
              👁️
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No users found.</p>
    </div>

    <div v-if="showHistory" class="modal">
      <div class="modal-content">
        <button class="close-btn" @click="closeHistory">X</button>
        <Userhistory :user-id="selectedUserId" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authFetch } from '../../../utils/authFetch.js'
import Loading from '../../../utils/Loading.vue'
import Userhistory from './user_history/Userhistory.vue'

const users = ref([])
const loading = ref(true)
const showHistory = ref(false)
const selectedUserId = ref(null)

const fetchUsers = async () => {
  try {
    const res = await authFetch('http://localhost:5000/getusers')
    const data = await res.json()
    users.value = data
  } catch (err) {
    console.error('Error fetching users:', err)
  } finally {
    loading.value = false
  }
}

const openHistory = (userId) => {
  selectedUserId.value = userId
  showHistory.value = true
}

const closeHistory = () => {
  showHistory.value = false
  selectedUserId.value = null
}

onMounted(fetchUsers)
</script>

<style scoped>
.view-users {
  padding: 20px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
th {
  background: #f5f5f5;
}
.view-icon {
  cursor: pointer;
  font-size: 1.2rem;
  text-align: center;
}
.view-icon:hover {
  color: #4c72e7;
}

/* Modal Styling */
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
  width: 80%;
  max-width: 800px;
  max-height: 90%;
  overflow: auto;
  position: relative;
}
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background: #ff4d4d;
  color: white;
  padding: 5px 10px;
  cursor: pointer;
}
</style>
