<template>
  <div class="dashboard-container" v-if="!loading">
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
      <component v-if="accessGranted" :is="activeTabComponent" />
      <div v-else class="error">Access Denied</div>
    </div>
  </div>

  <!-- Loading Spinner -->
  <Loading v-else />
</template>

<script>
import View_lots from './View Lots/View_lots.vue'
import Viewusers from './View Users/Viewusers.vue'
import Addlot from './Add Space/AddLot.vue'
import Editlot from './Edit Lot/Editlot.vue'
import ViewBookings from './ViewBookings/ViewBookings.vue'
import Loading from '../../Utils/Loading.vue'


export default {
  components: {
    View_lots,
    Addlot,
    Editlot,
    Loading,
    Viewusers,
    ViewBookings
  },
  data() {
    return {
      tabs: ['View Lots', 'Add Lot', 'Edit Lot Details', 'View Users', 'View Bookings', 'r'],
      activeTab: 'View Lots',
      loading: true,
      accessGranted: false
    }
  },
  computed: {
    activeTabComponent() {
      switch (this.activeTab) {
        case 'View Lots':
          return View_lots
        case 'Add Lot':
          return Addlot
        case 'Edit Lot Details':
          return Editlot
        case 'View Users':
          return Viewusers
        case 'View Bookings':
          return ViewBookings
        default:
          return null
      }
    }
  },
  methods: {
    setActive(tab) {
      this.activeTab = tab
    },
    async checkToken() {
      try {
        const res = await fetch('http://localhost:5000/parkinglots', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        this.accessGranted = res.ok;
        if (!res.ok) throw new Error('Unauthorized');
      } catch (e) {
        this.accessGranted = false;
        this.$router.push('/');
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.checkToken();
  }
}
</script>

<style scoped>
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

.error {
  text-align: center;
  color: red;
  font-weight: bold;
  font-size: 1.2rem;
}
</style>
