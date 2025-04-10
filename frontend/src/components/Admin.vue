<template>
  <div class="admin-container bg-dark text-white">
    <h1 class="text-center mb-5 text-light">Admin Dashboard - Evaluation Metrics</h1>

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
    <!-- Summary Charts Section -->
    <div class="summary-charts mb-5">
      <h2 class="text-center mb-4 text-light">Summary Charts</h2>
      <div class="row g-4">
        <!-- Precision Chart -->
        <div class="col-md-4">
          <div class="chart-container bg-secondary p-4 rounded">
            <h4 class="text-center mb-3">Precision@K</h4>
            <canvas ref="precisionChart"></canvas>
          </div>
        </div>

        <!-- MAP Chart -->
        <div class="col-md-4">
          <div class="chart-container bg-secondary p-4 rounded">
            <h4 class="text-center mb-3">MAP@K</h4>
            <canvas ref="mapChart"></canvas>
          </div>
        </div>

        <!-- Hit Rate Chart -->
        <div class="col-md-4">
          <div class="chart-container bg-secondary p-4 rounded">
            <h4 class="text-center mb-3">HitRate@K</h4>
            <canvas ref="hitRateChart"></canvas>
          </div>
        </div>
      </div>
    </div>
    <div class="summary-statistics mb-5">
      <h2 class="text-center mb-4 text-light">Summary Statistics</h2>
      <div class="row g-4">
        <!-- Precision Cards -->
        <div class="col-md-6 col-lg-3" v-for="k in [1, 3, 5, 10]" :key="'precision' + k">
          <div class="metric-card bg-gradient-blue rounded p-4">
            <h5 class="metric-title">Precision@{{ k }}</h5>
            <div class="metric-values">
              <div class="algorithm-metric">
                <span class="badge bg-primary me-2">TS</span>
                <span>{{ calculateAverage(`Thompson Sampling_Precision@K_@${k}`).toFixed(3) }}</span>
              </div>
              <div class="algorithm-metric">
                <span class="badge bg-danger me-2">EG</span>
                <span>{{ calculateAverage(`Epsilon-Greedy_Precision@K_@${k}`).toFixed(3) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- MAP Cards -->
        <div class="col-md-6 col-lg-3" v-for="k in [1, 3, 5, 10]" :key="'map' + k">
          <div class="metric-card bg-gradient-purple rounded p-4">
            <h5 class="metric-title">MAP@{{ k }}</h5>
            <div class="metric-values">
              <div class="algorithm-metric">
                <span class="badge bg-primary me-2">TS</span>
                <span>{{ calculateAverage(`Thompson Sampling_MAP@K_@${k}`).toFixed(3) }}</span>
              </div>
              <div class="algorithm-metric">
                <span class="badge bg-danger me-2">EG</span>
                <span>{{ calculateAverage(`Epsilon-Greedy_MAP@K_@${k}`).toFixed(3) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Hit Rate Cards -->
        <div class="col-md-6 col-lg-3" v-for="k in [1, 3, 5, 10]" :key="'hitrate' + k">
          <div class="metric-card bg-gradient-green rounded p-4">
            <h5 class="metric-title">HitRate@{{ k }}</h5>
            <div class="metric-values">
              <div class="algorithm-metric">
                <span class="badge bg-primary me-2">TS</span>
                <span>{{ calculateAverage(`Thompson Sampling_HitRate@K_@${k}`).toFixed(3) }}</span>
              </div>
              <div class="algorithm-metric">
                <span class="badge bg-danger me-2">EG</span>
                <span>{{ calculateAverage(`Epsilon-Greedy_HitRate@K_@${k}`).toFixed(3) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';

export default {
  name: 'AdminPage',
  data() {
    return {
      evaluations: {},
      charts: {
        precision: null,
        map: null,
        hitRate: null
      }
    };
  },
  async mounted() {
    await this.fetchEvaluationData();
    this.renderCharts();
  },
  methods: {
    async fetchEvaluationData() {
      try {
        const response = await axios.get('http://localhost:5000/evaluate');
        this.evaluations = response.data;
      } catch (error) {
        console.error('Error fetching evaluation data:', error);
      }
    },

    renderCharts() {
      // Destroy existing charts if they exist
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy();
      });

      // Prepare data for charts
      const ks = [1, 3, 5, 10];
      const algorithms = ['Thompson Sampling', 'Epsilon-Greedy'];

      // Precision Chart
      this.charts.precision = new Chart(this.$refs.precisionChart, {
        type: 'bar',
        data: this.getChartData('Precision@K', ks, algorithms),
        options: this.getChartOptions('Precision@K')
      });

      // MAP Chart
      this.charts.map = new Chart(this.$refs.mapChart, {
        type: 'bar',
        data: this.getChartData('MAP@K', ks, algorithms),
        options: this.getChartOptions('MAP@K')
      });

      // Hit Rate Chart
      this.charts.hitRate = new Chart(this.$refs.hitRateChart, {
        type: 'bar',
        data: this.getChartData('HitRate@K', ks, algorithms),
        options: this.getChartOptions('HitRate@K')
      });
    },

    getChartData(metricType, ks, algorithms) {
      const backgroundColors = [
        'rgba(54, 162, 235, 0.7)',  // Thompson Sampling (blue)
        'rgba(255, 99, 132, 0.7)'   // Epsilon-Greedy (red)
      ];

      return {
        labels: ks.map(k => `K=${k}`),
        datasets: algorithms.map((algo, idx) => ({
          label: algo,
          data: ks.map(k => this.calculateAverage(`${algo}_${metricType}_@${k}`)),
          backgroundColor: backgroundColors[idx],
          borderColor: backgroundColors[idx].replace('0.7', '1'),
          borderWidth: 1
        }))
      };
    },

    getChartOptions(title) {
      return {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#fff'
            }
          },
          title: {
            display: true,
            text: title,
            color: '#fff'
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${context.raw.toFixed(3)}`;
              }
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#fff'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          y: {
            min: 0,
            max: 1,
            ticks: {
              color: '#fff',
              stepSize: 0.2
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      };
    },

    calculateAverage(metricKey) {
      let sum = 0;
      let count = 0;

      for (const userData of Object.values(this.evaluations)) {
        if (userData[metricKey] !== undefined) {
          sum += parseFloat(userData[metricKey]);
          count++;
        }
      }

      return count > 0 ? sum / count : 0;
    },

    formatNumber(value) {
      if (value === undefined || value === null) return '-';
      return Number(value).toFixed(3);
    }
  },
  beforeUnmount() {
    // Clean up charts when component is destroyed
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy();
    });
  }
};
</script>

<style scoped>
.chart-container {
  height: 350px;
  position: relative;
}

.summary-charts {
  margin-bottom: 3rem;
}

/* Keep your existing styles */
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

.table th,
.table td {
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

/* Metric Cards Styling */
.metric-card {
  height: 100%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-title {
  font-size: 1.1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
  margin-bottom: 12px;
  color: white;
}

.metric-values {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.algorithm-metric {
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.bg-gradient-blue {
  background: linear-gradient(135deg, #3a3a3a, #1e3b70);
}

.bg-gradient-purple {
  background: linear-gradient(135deg, #3a3a3a, #4a1d6b);
}

.bg-gradient-green {
  background: linear-gradient(135deg, #3a3a3a, #1a5a3a);
}
</style>