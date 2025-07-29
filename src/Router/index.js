import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login/Login.vue'
import Admin_dashboard from '@/components/Admin Dashboard/Admin_dashboard.vue'
import User_Dashboard from '@/components/User Dashboard/User_Dashboard.vue'
import ViewBooking from '@/components/User Dashboard/View Booking/Viewbooking.vue'
// import BookingSummary from '../components/Email tickets/BookingSummary.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin_dashboard',
    name: 'AdminD',
    component: Admin_dashboard,
    meta: { requiresAdmin: true }
  },
  {
    path: '/user_dashboard',
    name: 'UserD',
    component: User_Dashboard
  },
  {
  path: '/userdashboard/viewbookings',
  component: ViewBooking
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem("role");  // or from store
  
  // Check if route meta requires admin
  if (to.meta.requiresAdmin && role !== "admin") {
    next("/user_dashboard");  // redirect normal users
  } else {
    next();  // allow navigation
  }
});


export default router
