<template>
    <div class="admin-report container py-4">
        <h2 class="mb-4">📊 Báo cáo thống kê hệ thống</h2>

        <!-- Thống kê tổng quan -->
        <div class="row mb-4">
            <div class="col-md-4" v-for="stat in stats" :key="stat.title">
                <div class="card shadow-sm text-center p-3">
                    <h5>{{ stat.title }}</h5>
                    <h3 class="text-primary">{{ stat.value }}</h3>
                </div>
            </div>
        </div>

        <!-- Biểu đồ -->
        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card p-3 shadow-sm">
                    <h6 class="mb-3">Số lượng học viên đăng ký theo tháng</h6>
                    <canvas id="studentChart"></canvas>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="card p-3 shadow-sm">
                    <h6 class="mb-3">Tỷ lệ Học viên / Giảng viên</h6>
                    <canvas id="userPieChart"></canvas>
                </div>
            </div>
            <div class="col-md-12 mb-4">
                <div class="card p-3 shadow-sm">
                    <h6 class="mb-3">Doanh thu theo tháng</h6>
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { onMounted, ref } from "vue";
import Chart from "chart.js/auto";

export default {
    name: "AdminReport",
    setup() {
        const stats = ref([
            { title: "👥 Người dùng", value: 1520 },
            { title: "📚 Khóa học", value: 230 },
            { title: "💰 Doanh thu (VNĐ)", value: "120,000,000" },
        ]);

        onMounted(() => {
            // Biểu đồ cột - Học viên theo tháng
            new Chart(document.getElementById("studentChart"), {
                type: "bar",
                data: {
                    labels: ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6"],
                    datasets: [
                        {
                            label: "Học viên mới",
                            data: [120, 150, 200, 180, 220, 300],
                            backgroundColor: "#42A5F5",
                        },
                    ],
                },
            });

            // Biểu đồ tròn - Tỷ lệ User
            new Chart(document.getElementById("userPieChart"), {
                type: "pie",
                data: {
                    labels: ["Học viên", "Giảng viên"],
                    datasets: [
                        {
                            data: [1300, 220],
                            backgroundColor: ["#66BB6A", "#FFA726"],
                        },
                    ],
                },
            });

            // Biểu đồ đường - Doanh thu
            new Chart(document.getElementById("revenueChart"), {
                type: "line",
                data: {
                    labels: ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6"],
                    datasets: [
                        {
                            label: "Doanh thu (VNĐ)",
                            data: [15000000, 20000000, 25000000, 18000000, 30000000, 35000000],
                            borderColor: "#EF5350",
                            fill: false,
                        },
                    ],
                },
            });
        });

        return { stats };
    },
};
</script>

<style scoped>
.admin-report {
    max-width: 1200px;
}

.card {
    border-radius: 12px;
}
</style>
