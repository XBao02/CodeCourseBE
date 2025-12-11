<template>
  <div class="reports-wrapper">
    <!-- Header -->
    <div class="reports-header">
      <h1>Instructor Reports</h1>
      <p>Overview of revenue and student progress</p>
    </div>

    <!-- Two main charts -->
    <div class="charts-grid two-cols">
      <!-- Total Revenue Chart -->
      <div class="chart-card">
        <h5>Total Revenue</h5>
        <line-chart v-if="revenueChartData && revenueChartData.labels?.length" :data="revenueChartData" />
        <p v-else class="no-data">No revenue data</p>
      </div>

      <!-- Student Completion vs In-Progress -->
      <div class="chart-card">
        <h5>Student Course Status</h5>
        <pie-chart v-if="completionChartData && completionChartData.datasets?.length" :data="completionChartData" />
        <p v-else class="no-data">No student progress data</p>
      </div>
    </div>
  </div>
</template>

<script>
import { getStoredSession } from '../../services/authService'
import LineChart from "../Instructor/LineChart.vue";
import PieChart from "../Instructor/PieChart.vue";

export default {
  name: 'InstructorReports',
  components: { LineChart, PieChart },
  data() {
    return {
      loading: false,
      error: false,
      revenueChartData: null,
      completionChartData: null,
    }
  },
  mounted() {
    this.loadReports()
  },
  methods: {
    getAuthHeaders() {
      const session = getStoredSession()
      if (!session?.access_token) return {}
      return { 'Authorization': `Bearer ${session.access_token}` }
    },
    async loadReports() {
      this.loading = true
      this.error = false
      try {
        const headers = this.getAuthHeaders()
        // Fetch revenue summary
        const revRes = await fetch('http://localhost:5000/api/instructor/reports/revenue', { headers })
        const progRes = await fetch('http://localhost:5000/api/instructor/reports/progress', { headers })

        const revJson = revRes.ok ? await revRes.json() : { points: [] }
        const progJson = progRes.ok ? await progRes.json() : { completed: 0, inProgress: 0 }

        // Build Line chart data: revenue over time (month -> amount)
        const labels = (revJson.points || []).map(p => p.label)
        const amounts = (revJson.points || []).map(p => p.amount || 0)
        this.revenueChartData = {
          labels,
          datasets: [
            {
              label: 'Revenue (VND)',
              data: amounts,
              borderColor: '#2563eb',
              backgroundColor: 'rgba(37,99,235,0.15)'
            }
          ]
        }

        // Build Pie chart data: completed vs in-progress
        const completed = progJson.completed || 0
        const inProgress = progJson.inProgress || 0
        this.completionChartData = {
          labels: ['Completed', 'In Progress'],
          datasets: [
            {
              data: [completed, inProgress],
              backgroundColor: ['#10b981', '#f59e0b']
            }
          ]
        }
      } catch (e) {
        console.error('Failed to load reports', e)
        this.error = true
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.reports-wrapper { background:#f8f9fa; min-height:100vh; padding:40px; }
.reports-header { margin-bottom:24px; }
.reports-header h1 { font-size:28px; font-weight:700; margin:0 0 6px; }
.reports-header p { color:#666; margin:0; }

.charts-grid.two-cols { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; }
.chart-card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:20px; }
.chart-card h5 { font-size:16px; font-weight:600; margin:0 0 12px; }
.no-data { color:#999; font-size:14px; }
</style>
