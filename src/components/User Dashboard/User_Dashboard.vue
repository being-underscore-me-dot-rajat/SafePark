<template>
<Loading v-if="loading" />
    <div v-else>
<div class="header">
      <div class="username">Welcome, {{ user.name }}</div>
    </div>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['sidebar-tab', { active: activeTab === tab }]"
        @click="setActive(tab)"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Content Pane -->
    <div class="pane-content">
      <component 
  :is="activeTabComponent" 
  v-if="activeTabComponent" 
  @booking-success="setActive('View Booking')" 
/>


      <div v-else>
        <h3>{{ activeTab }}</h3>
        <p>Content for this tab is not implemented yet.</p>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import Make_booking from './Make Booking/Make_booking.vue';
import View_booking from './View Booking/Viewbooking.vue';
import Loading from '../../Utils/Loading.vue'

export default {
    components: {
    Make_booking,
    View_booking,
    Loading
  },
  data() {
    return {
      tabs: [ 'Make Booking', 'View Booking', 'r'],
      activeTab: 'Make Booking',
      user:{},
      loading:true,
    }
  },
  computed: {
    activeTabComponent() {
      switch (this.activeTab) {
        case 'Make Booking':
          return Make_booking;
        case 'View Booking':
          return View_booking;

        default:
          return null;
      }
    }
  },
  methods: {
    setActive(tab) {
      this.activeTab = tab;
    }
  },
  mounted() {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      this.user = JSON.parse(storedUser);
    }
    this.loading=false;
  }
};
</script>

<style scoped>
.header {
  text-align: right;
  padding: 10px 20px;
  background-color: #eef2fb;
  font-weight: bold;
  color: #03438a;
}
.dashboard-container {
  display: flex;
  width: 95vw;
  height: 85vh;
  margin: 2rem auto;
  border: 2px solid #4c72e7;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(80, 100, 230, 0.07);
  background: #fafbff;
}

.sidebar {
  width: 120px;
  background: #eaf0fb;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  border-right: 5px solid #add8ff;
  box-shadow: 2px 0 8px #9ed0ff30;
}

.sidebar-tab {
  border: none;
  background: transparent;
  color: #22336b;
  font-size: 1rem;
  padding: 18px 0 18px 12px;
  text-align: left;
  cursor: pointer;
  position: relative;
  border-bottom: 1px solid #c9e1fa;
  transition: background 0.2s, color 0.2s;
}

.sidebar-tab.active,
.sidebar-tab:hover {
  background: #c8e0fe;
  color: #0353a8;
  font-weight: bold;
}

.pane-content {
  flex: 1;
  padding: 2rem;
}
</style>
