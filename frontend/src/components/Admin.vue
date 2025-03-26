<template>
    <div class="bg-dark text-white min-vh-100">
      <!-- Navbar -->
      <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
          <a class="navbar-brand" href="#">Music Recommendation - Admin</a>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <!-- Add any additional admin-specific links here -->
            </ul>
            <span class="navbar-text me-3">
              {{ username }}
            </span>
            <button class="btn btn-outline-light" @click="logout">Logout</button>
          </div>
        </div>
      </nav>
      
      <!-- Main Content -->
      <div class="container mt-5">
        <h2 class="text-center mb-4">User Evaluations</h2>
        <div v-if="evaluations && Object.keys(evaluations).length > 0">
          <!-- Precision Section -->
          <div class="mt-5">
            <h2 class="text-center mb-4">Precision per User (Latest)</h2>
            <ul class="list-group">
              <li class="list-group-item bg-dark text-white d-flex justify-content-between">
                <strong>User</strong>
                <strong>Thompson Sampling Precision</strong>
                <strong>Epsilon-Greedy Precision</strong>
              </li>
              <li v-for="(evaluation, username) in evaluations" :key="username" class="list-group-item bg-dark text-white d-flex justify-content-between">
                <span>{{ username }}</span>
                <span>{{ evaluation.ts_accuracy !== null ? evaluation.ts_accuracy.toFixed(2) : 'N/A' }}</span>
                <span>{{ evaluation.epsilon_greedy_accuracy !== null ? evaluation.epsilon_greedy_accuracy.toFixed(2) : 'N/A' }}</span>
              </li>
            </ul>
          </div>
          <!-- HitRate Section -->
          <div class="mt-5">
            <h2 class="text-center mb-4">HitRate@3 per User (Latest)</h2>
            <ul class="list-group">
              <li class="list-group-item bg-dark text-white d-flex justify-content-between">
                <strong>User</strong>
                <strong>Thompson Sampling HitRate@3</strong>
                <strong>Epsilon-Greedy HitRate@3</strong>
              </li>
              <li v-for="(evaluation, username) in evaluations" :key="username" class="list-group-item bg-dark text-white d-flex justify-content-between">
                <span>{{ username }}</span>
                <span>{{ evaluation.ts_hitrate_at_3 !== null ? evaluation.ts_hitrate_at_3.toFixed(2) : 'N/A' }}</span>
                <span>{{ evaluation.epsilon_greedy_hitrate_at_3 !== null ? evaluation.epsilon_greedy_hitrate_at_3.toFixed(2) : 'N/A' }}</span>
              </li>
            </ul>
          </div>
          <!-- Combined Accuracy Section -->
          <div class="mt-5">
            <h2 class="text-center mb-4">Combined Accuracy and HitRate@3</h2>
            <ul class="list-group">
              <li class="list-group-item bg-dark text-white">
                <strong>Combined Thompson Sampling Accuracy:</strong> {{ combinedAccuracy.combined_ts_accuracy.toFixed(2) }}
              </li>
              <li class="list-group-item bg-dark text-white">
                <strong>Combined Epsilon-Greedy Accuracy:</strong> {{ combinedAccuracy.combined_epsilon_greedy_accuracy.toFixed(2) }}
              </li>
              <li class="list-group-item bg-dark text-white">
                <strong>Combined Thompson Sampling HitRate@3:</strong> {{ combinedAccuracy.combined_ts_hitrate_at_3.toFixed(2) }}
              </li>
              <li class="list-group-item bg-dark text-white">
                <strong>Combined Epsilon-Greedy HitRate@3:</strong> {{ combinedAccuracy.combined_epsilon_greedy_hitrate_at_3.toFixed(2) }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else>
          <p class="text-center">No evaluations available.</p>
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
        evaluations: {},
        combinedAccuracy: {}
      };
    },
    methods: {
      fetchEvaluations() {
        axios.get('http://localhost:5000/evaluate')
          .then(response => {
            this.evaluations = response.data;
          })
          .catch(error => {
            console.error("Error fetching evaluations:", error);
          });
      },
      fetchCombinedAccuracy() {
        axios.get('http://localhost:5000/combined_accuracy')
          .then(response => {
            this.combinedAccuracy = response.data;
          })
          .catch(error => {
            console.error("Error fetching combined accuracy:", error);
          });
      },
      logout() {
        axios.post('http://localhost:5000/logout')
          .then(response => {
            if (response.status === 200) {
              this.$router.push('/login');
            }
          })
          .catch(error => {
            console.error("Error logging out:", error);
          });
      }
    },
    created() {
      axios.get('http://localhost:5000/profile')
        .then(response => {
          if (response.status === 200) {
            this.username = response.data.message.split(' ')[1];
          } else {
            this.$router.push('/login');
          }
        })
        .catch(error => {
          console.error("Error fetching profile:", error);
          this.$router.push('/login');
        });
  
      this.fetchEvaluations();
      this.fetchCombinedAccuracy();
    }
  };
  </script>
  
  <style scoped>
  html, body {
    height: 100%;
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background-color: #121212;
    color: #ffffff;
  }
  
  .container {
    margin-top: 50px;
  }
  
  .bg-dark {
    background-color: #343a40 !important;
  }
  
  .text-white {
    color: #fff !important;
  }
  
  .btn-light {
    background-color: #f8f9fa;
    border-color: #f8f9fa;
    color: #212529;
  }
  
  .btn-outline-light {
    border-color: #f8f9fa;
    color: #f8f9fa;
  }
  
  .btn-outline-light:hover {
    background-color: #f8f9fa;
    color: #212529;
  }
  </style>