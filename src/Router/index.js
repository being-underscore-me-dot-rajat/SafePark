import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login/Login.vue'
import Admin_dashboard from '@/components/Admin Dashboard/Admin_dashboard.vue'
import User_Dashboard from '@/components/User Dashboard/User_Dashboard.vue'
import ViewBooking from '@/components/User Dashboard/View Booking/Viewbooking.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin_dashboard',
    name: 'AdminD',
    component: Admin_dashboard
  },
  {
    path: '/user_dashboard',
    name: 'UserD',
    component: User_Dashboard
  },
  {
  path: '/userdashboard/viewbookings',
  component: ViewBooking
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
