<template>
    <div class="container mt-5">
      <h2 class="text-center mb-4">Register</h2>
      <div class="row justify-content-center">
        <div class="col-md-6">
          <form @submit.prevent="register">
            <div class="mb-3">
              <label for="username" class="form-label">Username</label>
              <input type="text" class="form-control" id="username" v-model="username" required>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Register</button>
          </form>
          <p class="mt-3 text-center">
            Already have an account? <router-link to="/login">Login</router-link>
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
      register() {
        axios.post('http://localhost:5000/register', {
          username: this.username,
          password: this.password
        }).then(response => {
          if (response.status === 201) {
            this.$router.push('/login');
          }
        }).catch(error => {
          console.error("Error during registration:", error);
          alert("Username already exists!");
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