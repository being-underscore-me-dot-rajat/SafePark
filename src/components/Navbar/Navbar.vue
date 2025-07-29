<template>
  <nav class="navbar">
  <div class="logo"  @click="home">
  <img src="/public\logo_withoutbg.png" id="logoimg"><p id="logotxt">SafePark</p></div>
    <ul class="nav-links">
      <li class="nav-item logout" @click="logout">Logout</li>
    </ul>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const home = () => {
  if (localStorage.role=="admin"){
    router.push('/admin_dashboard');
  }
  else{
    router.push('/user_dashboard');
  }
  
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/') 
}
</script>


<style scoped>
#logoimg{
  height:3rem;
}
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #819ab4ff;
  color: white;
}

.logo {
  font-weight: bold;
  font-size: 1.4rem;
  display:flex;
  border: 1px solid black;
  padding:2px;
  border-width: 2px;
  border-radius: 10px;
  background-color: #90a1b2ff;
  box-shadow: 0px 3px 0px rgba(0, 0, 0, 0.3);
}

#logotxt{
  margin:1rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
  font-size:1rem;
}

.nav-item {
  color: white;
  text-decoration: none;
  position: relative;
  padding-bottom: 3px;
  font-size:1.5rem;
}

.nav-item::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #193832ff;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
}

.nav-item:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
</style>
