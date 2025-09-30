<template>
  <div>
    <LineChartGenerator :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from "chart.js";
import { Line as LineChartGenerator } from "vue-chartjs";

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale);

export default {
  name: "LineChart",
  props: {
    data: { type: Array, required: true }
  },
  computed: {
    chartData() {
      return {
        labels: ["Th1","Th2","Th3","Th4","Th5","Th6","Th7","Th8","Th9","Th10","Th11","Th12"],
        datasets: [
          {
            label: "Số học viên",
            data: this.data,
            borderColor: "#6FDB6A",
            backgroundColor: "rgba(111,219,106,0.2)",
            tension: 0.3,
            fill: true
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
  components: { LineChartGenerator }
};
</script>

<style scoped>
div {
  height: 280px;
}
</style>
