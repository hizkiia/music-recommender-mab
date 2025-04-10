<template>
  <div class="admin-container bg-dark text-white">
    <h1 class="text-center mb-5 text-light">📊 Admin Dashboard - Evaluation Metrics</h1>

    <!-- Section Precision -->
    <div class="metrics-section bg-secondary shadow-sm rounded mb-5 p-4">
      <h2 class="section-title">Precision@K</h2>
      <table class="metrics-table table table-dark table-hover table-bordered rounded">
        <thead>
          <tr>
            <th>User</th>
            <th>Algorithm</th>
            <th>K=1</th>
            <th>K=3</th>
            <th>K=5</th>
            <th>K=10</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(userData, username) in evaluations" :key="username">
            <tr>
              <td rowspan="2" class="align-middle">{{ username }}</td>
              <td>Thompson Sampling</td>
              <td>{{ formatNumber(userData['Thompson Sampling_Precision@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_Precision@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_Precision@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_Precision@K_@10']) }}</td>
            </tr>
            <tr>
              <td>Epsilon-Greedy</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_Precision@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_Precision@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_Precision@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_Precision@K_@10']) }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Section MAP -->
    <div class="metrics-section bg-secondary shadow-sm rounded mb-5 p-4">
      <h2 class="section-title">MAP@K</h2>
      <table class="metrics-table table table-dark table-hover table-bordered rounded">
        <thead>
          <tr>
            <th>User</th>
            <th>Algorithm</th>
            <th>K=1</th>
            <th>K=3</th>
            <th>K=5</th>
            <th>K=10</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(userData, username) in evaluations" :key="username">
            <tr>
              <td rowspan="2" class="align-middle">{{ username }}</td>
              <td>Thompson Sampling</td>
              <td>{{ formatNumber(userData['Thompson Sampling_MAP@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_MAP@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_MAP@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_MAP@K_@10']) }}</td>
            </tr>
            <tr>
              <td>Epsilon-Greedy</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_MAP@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_MAP@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_MAP@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_MAP@K_@10']) }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Section HitRate -->
    <div class="metrics-section bg-secondary shadow-sm rounded mb-5 p-4">
      <h2 class="section-title">HitRate@K</h2>
      <table class="metrics-table table table-dark table-hover table-bordered rounded">
        <thead>
          <tr>
            <th>User</th>
            <th>Algorithm</th>
            <th>K=1</th>
            <th>K=3</th>
            <th>K=5</th>
            <th>K=10</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(userData, username) in evaluations" :key="username">
            <tr>
              <td rowspan="2" class="align-middle">{{ username }}</td>
              <td>Thompson Sampling</td>
              <td>{{ formatNumber(userData['Thompson Sampling_HitRate@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_HitRate@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_HitRate@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Thompson Sampling_HitRate@K_@10']) }}</td>
            </tr>
            <tr>
              <td>Epsilon-Greedy</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_HitRate@K_@1']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_HitRate@K_@3']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_HitRate@K_@5']) }}</td>
              <td>{{ formatNumber(userData['Epsilon-Greedy_HitRate@K_@10']) }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Summary Cards -->
    <div class="summary-section">
      <h2 class="text-center mb-4 text-light">Summary Statistics</h2>
      <div class="summary-cards d-flex flex-wrap gap-4 justify-content-center">
        <div class="summary-card bg-gradient rounded text-white p-4">
          <h4>Average Precision@10</h4>
          <p>Thompson: {{ calculateAverage('Thompson Sampling_Precision@K_@10') }}</p>
          <p>Epsilon: {{ calculateAverage('Epsilon-Greedy_Precision@K_@10') }}</p>
        </div>
        <div class="summary-card bg-gradient rounded text-white p-4">
          <h4>Average MAP@10</h4>
          <p>Thompson: {{ calculateAverage('Thompson Sampling_MAP@K_@10') }}</p>
          <p>Epsilon: {{ calculateAverage('Epsilon-Greedy_MAP@K_@10') }}</p>
        </div>
        <div class="summary-card bg-gradient rounded text-white p-4">
          <h4>Average HitRate@3</h4>
          <p>Thompson: {{ calculateAverage('Thompson Sampling_HitRate@K_@3') }}</p>
          <p>Epsilon: {{ calculateAverage('Epsilon-Greedy_HitRate@K_@3') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminPage',
  data() {
    return {
      evaluations: {}
    };
  },
  async created() {
    await this.fetchEvaluationData();
  },
  methods: {
    async fetchEvaluationData() {
      try {
        const response = await axios.get('http://localhost:5000/evaluate', {
          withCredentials: true
        });
        this.evaluations = response.data;
      } catch (error) {
        console.error('Error fetching evaluation data:', error);
      }
    },
    formatNumber(value) {
      if (value === undefined || value === null) return '-';
      return Number(value).toFixed(3);
    },
    calculateAverage(metricKey) {
      let sum = 0;
      let count = 0;
      
      for (const userData of Object.values(this.evaluations)) {
        if (userData[metricKey] !== undefined) {
          sum += userData[metricKey];
          count++;
        }
      }
      
      return count > 0 ? (sum / count).toFixed(3) : '0.000';
    }
  }
};
</script>





<style scoped>
.admin-container {
  padding: 40px 20px;
  min-height: 100vh;
  background-color: #121212;
  color: #ffffff;
}

.section-title {
  color: #ffffff;
  border-bottom: 2px solid #4e8cff;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.table th {
  background-color: #1f1f1f;
  color: #dcdcdc;
}

.table td {
  background-color: #2a2a2a;
}

.table th, .table td {
  vertical-align: middle;
}

.summary-cards {
  gap: 2rem;
}

.summary-card {
  min-width: 250px;
  max-width: 320px;
  background: linear-gradient(135deg, #3a3a3a, #1e1e1e);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.summary-card h4 {
  border-bottom: 1px solid #777;
  padding-bottom: 10px;
  margin-bottom: 15px;
  font-size: 1.25rem;
}

.summary-card p {
  font-size: 0.95rem;
  margin-bottom: 8px;
}
</style>
