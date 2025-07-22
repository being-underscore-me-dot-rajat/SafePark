<template>
  <div class="auth-box">
    <h2>{{ isLogin ? 'Login' : 'Register' }}</h2>

    <form @submit.prevent="isLogin ? handleLogin() : handleRegister()">
      <div v-if="!isLogin" class="input-group">
        <label>Name</label>
        <input type="text" v-model="name" required />
      </div>

      <div class="input-group">
        <label>Email</label>
        <input type="email" v-model="email" required />
      </div>

      <div class="input-group">
        <label>Password</label>
        <input type="password" v-model="password" required />
      </div>

      <button type="submit">{{ isLogin ? 'Login' : 'Register' }}</button>
    </form>

    <p class="toggle-link">
      {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
      <a href="#" @click.prevent="isLogin = !isLogin">
        {{ isLogin ? 'Register here' : 'Login here' }}
      </a>
    </p>

  </div>
  <div v-if="showOtpBox" class="input-group">
    <label>Enter OTP sent to email</label>
    <input type="text" v-model="otp" maxlength="6" />
    <button @click="verifyOtp">Verify OTP</button>
  </div>
  <div v-if="showMessage" class="toast">{{ message }}</div>

</template>

<script>
export default {
  data() {
    return {
      isLogin: true,
      name: '',
      email: '',
      password: '',
      otp: '',
      showOtpBox: false,
      message: '',
      showMessage: false
    }
  },
  methods: {
    showNotification(msg) {
      this.message = msg;
      this.showMessage = true;
      setTimeout(() => {
        this.showMessage = false;
        this.message = '';
      }, 10000);
    },

    async handleLogin() {
      try {
        const response = await fetch('http://localhost:5000/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        });

        const data = await response.json();

        if (response.status === 403 && data.require_otp) {
          this.showOtpBox = true;
          this.showNotification("Email not verified. Please enter the OTP sent to your email.", "warning");
          return;
        }

        if (!response.ok) throw new Error(data.message || 'Login failed');
        this.showNotification(data.message, "success");
        if (response.ok) {
          localStorage.setItem('token', data.token); 
          localStorage.setItem('user', JSON.stringify(data.user));
        }


        if (data.user.role === 'admin') {
          this.$router.push('/admin_dashboard');
        } else if (data.user.role === 'user') {
          this.$router.push('/user_dashboard');
        }

      } catch (err) {
        this.showNotification(err.message || 'Login failed', "error");
      }
    },


    async handleRegister() {
      try {
        const response = await fetch('http://localhost:5000/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.name,
            email: this.email,
            password: this.password
          })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.message || data.error);

        this.showOtpBox = true;
        this.showNotification("OTP sent to your email. Please verify.");
      } catch (err) {
        this.showNotification(err.message || 'Registration failed');
      }
    },
    async verifyOtp() {
      try {
        const response = await fetch('http://localhost:5000/verify-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            otp: this.otp
          })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.message || data.error);

        this.showNotification(data.message);
        this.showOtpBox = false;
        this.isLogin = true;
      } catch (err) {
        this.showNotification(err.message || 'OTP verification failed');
      }
    }
  }
}

</script>

<style scoped>
.auth-box {
  max-width: 350px;
  margin: 40px auto;
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  background: #fff;
}

.auth-box h2 {
  text-align: center;
  margin-bottom: 16px;
}

.input-group {
  margin-bottom: 12px;
}

.input-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
}

.input-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #aaa;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background-color: #369f76;
}

.toggle-link {
  text-align: center;
  margin-top: 12px;
  font-size: 0.9rem;
}

.toggle-link a {
  color: #42b983;
  font-weight: bold;
  text-decoration: none;
  margin-left: 4px;
}

.toggle-link a:hover {
  text-decoration: underline;
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #42b983;
  color: white;
  padding: 12px 18px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: opacity 0.5s;
  z-index: 9999;
}
</style>
