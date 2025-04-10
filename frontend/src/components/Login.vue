<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center min-vh-100">
    <div class="auth-card shadow-lg rounded p-4 bg-dark text-white" style="width: 100%; max-width: 400px;">
      <h2 class="text-center mb-4">Welcome Back</h2>
      <form @submit.prevent="login">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input type="text" class="form-control bg-secondary border-0 text-white" id="username" v-model="username" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control bg-secondary border-0 text-white" id="password" v-model="password" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
      <p class="mt-3 text-center text-muted">
        Don't have an account? <router-link to="/register" class="text-decoration-none text-info">Register</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  methods: {
    login() {
      axios.post('http://localhost:5000/login', {
        username: this.username,
        password: this.password
      }, {
        withCredentials: true
      }).then(response => {
        if (response.status === 200) {
          this.$router.push('/recommend');
        }
      }).catch(error => {
        console.error("Error during login:", error);
        alert("Invalid username or password!");
      });
    }
  }
};
</script>

<style scoped>
.auth-wrapper {
  background-color: #1a1a2e;
  padding: 2rem;
}

.auth-card {
  background-color: #2e3548;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.form-control:focus {
  box-shadow: none;
  border-color: #4e8cff;
}

.btn-primary {
  background-color: #4e8cff;
  border-color: #4e8cff;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #366fdd;
  border-color: #366fdd;
}
</style>
