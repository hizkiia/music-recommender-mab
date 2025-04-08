<template>
    <div class="container mt-5">
      <h2 class="text-center mb-4">Login</h2>
      <div class="row justify-content-center">
        <div class="col-md-6">
          <form @submit.prevent="login">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input type="text" class="form-control" id="username" v-model="username" required>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
          </form>
          <p class="mt-3 text-center">
            Don't have an account? <router-link to="/register">Register</router-link>
          </p>
        </div>
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
  .container {
    margin-top: 100px;
  }
  </style>