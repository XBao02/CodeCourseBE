<template>
  <div>
    <PieChartGenerator :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from "chart.js";
import { Pie as PieChartGenerator } from "vue-chartjs";

ChartJS.register(Title, Tooltip, Legend, ArcElement);

export default {
  name: "PieChart",
  props: {
    data: { type: Object, required: true }
  },
  computed: {
    chartData() {
      return {
        labels: ["Hoàn thành", "Bỏ dở", "Đang học"],
        datasets: [
          {
            backgroundColor: ["#6FDB6A", "#ff6384", "#36a2eb"],
            data: [this.data.completed, this.data.dropped, this.data.inProgress]
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
  components: { PieChartGenerator }
};
</script>

<style scoped>
div {
  height: 280px;
}
</style>
