<template>
  <div class="admin-container">
    <h1>Admin Dashboard - Evaluation Metrics</h1>
    
    <!-- Section Precision -->
    <div class="metrics-section">
      <h2>Precision@K</h2>
      <table class="metrics-table">
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
              <td rowspan="2">{{ username }}</td>
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
    <div class="metrics-section">
      <h2>MAP@K</h2>
      <table class="metrics-table">
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
              <td rowspan="2">{{ username }}</td>
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
    <div class="metrics-section">
      <h2>HitRate@K</h2>
      <table class="metrics-table">
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
              <td rowspan="2">{{ username }}</td>
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
    
    <!-- Summary Statistics -->
    <div class="summary-section">
      <h2>Summary Statistics</h2>
      <div class="summary-cards">
        <div class="summary-card">
          <h3>Average Precision@10</h3>
          <p>Thompson Sampling: {{ calculateAverage('Thompson Sampling_Precision@K_@10') }}</p>
          <p>Epsilon-Greedy: {{ calculateAverage('Epsilon-Greedy_Precision@K_@10') }}</p>
        </div>
        <div class="summary-card">
          <h3>Average MAP@10</h3>
          <p>Thompson Sampling: {{ calculateAverage('Thompson Sampling_MAP@K_@10') }}</p>
          <p>Epsilon-Greedy: {{ calculateAverage('Epsilon-Greedy_MAP@K_@10') }}</p>
        </div>
        <div class="summary-card">
          <h3>Average HitRate@3</h3>
          <p>Thompson Sampling: {{ calculateAverage('Thompson Sampling_HitRate@K_@3') }}</p>
          <p>Epsilon-Greedy: {{ calculateAverage('Epsilon-Greedy_HitRate@K_@3') }}</p>
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
/* Tetap gunakan style yang sama seperti sebelumnya */
.admin-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.metrics-section {
  margin-bottom: 40px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h2 {
  color: #444;
  margin-bottom: 15px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.metrics-table th, .metrics-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.metrics-table th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.metrics-table tr:hover {
  background-color: #f5f5f5;
}

.summary-section {
  margin-top: 40px;
  background: #f0f8ff;
  padding: 20px;
  border-radius: 8px;
}

.summary-cards {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

.summary-card {
  flex: 1;
  min-width: 250px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-card h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.summary-card p {
  margin: 8px 0;
  color: #555;
}
</style>
