<template>
  <nav class="navbar">
    <div class="logo">MySite</div>
    <ul class="nav-links">
      <li class="nav-item">Home</li>
      <li class="nav-item">About</li>
      <li class="nav-item">Contact</li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2c3e50;
  color: white;
}

.logo {
  font-weight: bold;
  font-size: 1.4rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
}

.nav-item {
  color: white;
  text-decoration: none;
  position: relative;
  padding-bottom: 3px;
}

.nav-item::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #1abc9c;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
}

.nav-item:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
</style>
