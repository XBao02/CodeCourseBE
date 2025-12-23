<template>
  <div>
    <BarChartGenerator :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from "chart.js";
import { Bar as BarChartGenerator } from "vue-chartjs";

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default {
  name: "BarChart",
  props: {
    data: { type: Array, required: true }
  },
  computed: {
    chartData() {
      return {
        labels: this.data.map(d => d.label),
        datasets: [          {
            label: "Quiz",
            data: this.data.map(d => d.quiz),
            backgroundColor: "#6FDB6A"
          },
          {
            label: "Lab",
            data: this.data.map(d => d.lab),
            backgroundColor: "#36a2eb"
          }
        ]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false
      };
    }
  },
  components: { BarChartGenerator }
};
</script>

<style scoped>
div {
  height: 280px;
}
</style>
