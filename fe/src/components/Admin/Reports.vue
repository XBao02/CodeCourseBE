<template>
    <div class="admin-report">
        <!-- Header -->
        <div class="report-header">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="report-title">Báo cáo thống kê hệ thống</h1>
                        <p class="report-subtitle">Tổng quan hiệu suất nền tảng học tập</p>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="header-actions">
                            <select class="form-select period-select" v-model="selectedPeriod">
                                <option value="7days">7 ngày qua</option>
                                <option value="30days" selected>30 ngày qua</option>
                                <option value="90days">90 ngày qua</option>
                                <option value="1year">1 năm qua</option>
                            </select>
                            <button class="btn btn-export">
                                <i class="fas fa-download me-2"></i>Xuất báo cáo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="container">
            <!-- Thống kê tổng quan -->
            <div class="stats-section">
                <div class="row g-4">
                    <div class="col-md-4" v-for="stat in stats" :key="stat.title">
                        <div class="stat-card" :class="`stat-${stat.type}`">
                            <div class="stat-icon">
                                <i :class="stat.icon"></i>
                            </div>
                            <div class="stat-content">
                                <h5>{{ stat.title }}</h5>
                                <h3 class="stat-value">{{ stat.value }}</h3>
                                <div class="stat-trend" :class="stat.trend.type">
                                    <i :class="stat.trend.icon"></i>
                                    <span>{{ stat.trend.value }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Biểu đồ -->
            <div class="charts-section">
                <div class="row g-4">
                    <!-- Biểu đồ học viên -->
                    <div class="col-lg-6">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5 class="chart-title">Số lượng học viên đăng ký theo tháng</h5>
                                <div class="chart-actions">
                                    <button class="btn btn-period" :class="{ active: registrationMode === 'month' }" @click="changeRegistrationMode('month')">Tháng</button>
                                    <button class="btn btn-period" :class="{ active: registrationMode === 'quarter' }" @click="changeRegistrationMode('quarter')">Quý</button>
                                    <button class="btn btn-period" :class="{ active: registrationMode === 'year' }" @click="changeRegistrationMode('year')">Năm</button>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas ref="studentChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Biểu đồ tỷ lệ user -->
                    <div class="col-lg-6">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5 class="chart-title">Phân bổ người dùng</h5>
                                <div class="chart-info">
                                    <span class="total-users">{{ totalUsersLabel }}</span>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas ref="userPieChart"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Biểu đồ doanh thu -->
                    <div class="col-12">
                        <div class="chart-card">
                            <div class="chart-header">
                                <h5 class="chart-title">Doanh thu theo tháng</h5>
                                <div class="chart-actions">
                                    <button
                                        v-for="year in revenueYears"
                                        :key="year"
                                        class="btn btn-period"
                                        :class="{ active: selectedRevenueYear === year }"
                                        @click="changeRevenueYear(year)"
                                    >
                                        {{ year }}
                                    </button>
                                </div>
                            </div>
                            <div class="chart-container">
                                <canvas ref="revenueChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Additional Metrics -->
            <div class="metrics-section">
                <div class="row g-4">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-icon completion">
                                <i class="fas fa-trophy"></i>
                            </div>
                            <div class="metric-content">
                                <h4>{{ summaryMetrics.completionRate }}%</h4>
                                <p>Tỷ lệ hoàn thành</p>
                                <span class="metric-trend up">DB</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-icon rating">
                                <i class="fas fa-star"></i>
                            </div>
                            <div class="metric-content">
                                <h4>{{ summaryMetrics.averageScore }}/10</h4>
                                <p>Điểm trung bình</p>
                                <span class="metric-trend up">DB</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-icon time">
                                <i class="fas fa-clock"></i>
                            </div>
                            <div class="metric-content">
                                <h4>{{ summaryMetrics.averageProgress }}%</h4>
                                <p>Tiến độ trung bình</p>
                                <span class="metric-trend up">DB</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-icon engagement">
                                <i class="fas fa-share-alt"></i>
                            </div>
                            <div class="metric-content">
                                <h4>{{ summaryMetrics.engagementCount }}</h4>
                                <p>Tin nhắn/Engagement</p>
                                <span class="metric-trend up">DB</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { onMounted, ref, onBeforeUnmount } from "vue";
import Chart from "chart.js/auto";
import adminService from "@/services/adminService";

export default {
    name: "AdminReport",
    setup() {
        const selectedPeriod = ref('30days');
        const selectedRevenueYear = ref('2025');
        const revenueYears = ['2025', '2024', '2023', '2022'];
        const studentChart = ref(null);
        const userPieChart = ref(null);
        const revenueChart = ref(null);

        const stats = ref([]);
        const totalUsersLabel = ref('');
        const registrationMode = ref('month');
        const analyticsData = ref(null);
        const summaryMetrics = ref({
            completionRate: 0,
            averageScore: 0,
            averageProgress: 0,
            engagementCount: 0
        });

        let studentChartInstance = null;
        let userPieChartInstance = null;
        let revenueChartInstance = null;

        const buildStats = (summary) => {
            const fmt = (n) => Number(n || 0).toLocaleString();
            return [
                { 
                    title: "Người dùng", 
                    value: fmt(summary.students + summary.instructors + 1), // +1 admin tối thiểu
                    type: "users",
                    icon: "fas fa-users",
                    trend: { value: "", type: "up", icon: "fas fa-arrow-up" }
                },
                { 
                    title: "Khóa học", 
                    value: fmt(summary.courses), 
                    type: "courses",
                    icon: "fas fa-book-open",
                    trend: { value: "", type: "up", icon: "fas fa-arrow-up" }
                },
                { 
                    title: "Đang hoạt động", 
                    value: fmt(summary.activeCourses), 
                    type: "revenue",
                    icon: "fas fa-chart-line",
                    trend: { value: "", type: "up", icon: "fas fa-arrow-up" }
                }
            ];
        };

        const buildRegistrationDataset = () => {
            const months = analyticsData.value?.registrationsByMonth || [];
            if (registrationMode.value === 'month') {
                return {
                    labels: ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12"],
                    data: months
                };
            }
            if (registrationMode.value === 'quarter') {
                const quarters = [0, 0, 0, 0];
                months.forEach((val, idx) => {
                    const q = Math.floor(idx / 3);
                    quarters[q] += Number(val || 0);
                });
                return { labels: ["Q1", "Q2", "Q3", "Q4"], data: quarters };
            }
            const total = months.reduce((s, v) => s + Number(v || 0), 0);
            return { labels: [`${selectedRevenueYear.value}`], data: [total] };
        };

        const initRegistrationChart = () => {
            const { labels, data } = buildRegistrationDataset();
            const ctxStudent = studentChart.value?.getContext("2d");
            if (studentChartInstance) studentChartInstance.destroy();
            studentChartInstance = new Chart(ctxStudent, {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Học viên mới",
                            data,
                            backgroundColor: "#4f46e5",
                            borderRadius: 6,
                            borderSkipped: false,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: "rgba(0, 0, 0, 0.05)" } },
                        x: { grid: { display: false } }
                    }
                }
            });
        };

        const initCharts = (analytics, summary) => {
            analyticsData.value = analytics;
            initRegistrationChart();

            const ctxPie = userPieChart.value?.getContext("2d");
            if (userPieChartInstance) userPieChartInstance.destroy();
            const dist = summary.studentDistribution || {};
            const totalUsers = Number(summary.students || 0) + Number(summary.instructors || 0) + 1; // add admin
            totalUsersLabel.value = `Tổng: ${totalUsers.toLocaleString()} users`;
            userPieChartInstance = new Chart(ctxPie, {
                type: "doughnut",
                data: {
                    labels: ["Hoàn thành", "Đang học", "Đã hủy"],
                    datasets: [
                        {
                            data: [
                                Number(dist.completed || 0),
                                Number(dist.inProgress || 0),
                                Number(dist.dropped || 0)
                            ],
                            backgroundColor: ["#4f46e5", "#10b981", "#f59e0b"],
                            borderWidth: 0,
                            borderRadius: 8,
                            spacing: 4
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { usePointStyle: true, padding: 20, font: { size: 12 } }
                        }
                    }
                }
            });

            const ctxRevenue = revenueChart.value?.getContext("2d");
            if (revenueChartInstance) revenueChartInstance.destroy();
            revenueChartInstance = new Chart(ctxRevenue, {
                type: "line",
                data: {
                    labels: ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12"],
                    datasets: [
                        {
                            label: "Doanh thu ($)",
                            data: analytics.revenueByMonth || [],
                            borderColor: "#ef4444",
                            backgroundColor: "rgba(239, 68, 68, 0.1)",
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: "#ef4444",
                            pointBorderColor: "#ffffff",
                            pointBorderWidth: 2,
                            pointRadius: 5,
                            pointHoverRadius: 7
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: "rgba(0, 0, 0, 0.05)" },
                            ticks: { callback: (v) => '$' + v }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        };

        const loadData = async () => {
            try {
                const [summary, analytics] = await Promise.all([
                    adminService.getReportsSummary(),
                    adminService.getDashboardAnalytics(selectedRevenueYear.value)
                ]);
                stats.value = buildStats(summary);
                summaryMetrics.value = {
                    completionRate: summary.completionRate || 0,
                    averageScore: (summary.averageScore || 0).toFixed(1),
                    averageProgress: summary.averageProgress || 0,
                    engagementCount: summary.engagementCount || 0
                }
                initCharts(analytics, summary);
            } catch (error) {
                console.error("Failed to load report data", error);
            }
        };

        const changeRevenueYear = (year) => {
            if (selectedRevenueYear.value === year) return;
            selectedRevenueYear.value = year;
            loadData();
        };

        const changeRegistrationMode = (mode) => {
            registrationMode.value = mode;
            if (analyticsData.value) {
                initRegistrationChart();
            }
        };

        onMounted(() => {
            loadData();
        });

        onBeforeUnmount(() => {
            if (studentChartInstance) studentChartInstance.destroy();
            if (userPieChartInstance) userPieChartInstance.destroy();
            if (revenueChartInstance) revenueChartInstance.destroy();
        });

        return { 
            stats, 
            selectedPeriod,
            selectedRevenueYear,
            revenueYears,
            studentChart,
            userPieChart,
            revenueChart,
            totalUsersLabel,
            registrationMode,
            changeRegistrationMode,
            changeRevenueYear,
            summaryMetrics
        };
    },
};
</script>

<style scoped>
.admin-report {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    min-height: 100vh;
    padding: 2rem 0;
}

/* Header */
.report-header {
    background: white;
    padding: 2rem 0;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    border-bottom: 1px solid #e9ecef;
}

.report-title {
    font-size: 2.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
}

.report-subtitle {
    color: #64748b;
    font-size: 1.1rem;
    margin: 0;
}

.header-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.period-select {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    background: white;
    min-width: 150px;
}

.btn-export {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-export:hover {
    background: #4338ca;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* Stats Section */
.stats-section {
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    height: 100%;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.stat-icon {
    width: 70px;
    height: 70px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;
}

.stat-users .stat-icon { background: linear-gradient(135deg, #4f46e5, #6366f1); }
.stat-courses .stat-icon { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-revenue .stat-icon { background: linear-gradient(135deg, #f59e0b, #fbbf24); }

.stat-content h5 {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 2.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
}

.stat-trend {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.stat-trend.up {
    color: #10b981;
}

.stat-trend.down {
    color: #ef4444;
}

/* Charts Section */
.charts-section {
    margin-bottom: 2rem;
}

.chart-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    height: 100%;
}

.chart-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.chart-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
}

.chart-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-period {
    border: 1px solid #e2e8f0;
    background: white;
    color: #64748b;
    padding: 0.375rem 0.75rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-period.active,
.btn-period:hover {
    background: #4f46e5;
    color: white;
    border-color: #4f46e5;
}

.chart-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.total-users {
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
}

.chart-container {
    height: 300px;
    position: relative;
}

/* Metrics Section */
.metrics-section {
    margin-top: 2rem;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    text-align: center;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-icon {
    width: 50px;
    height: 50px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    color: white;
    margin: 0 auto 1rem;
}

.metric-icon.completion { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.metric-icon.rating { background: linear-gradient(135deg, #ef4444, #f87171); }
.metric-icon.time { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.metric-icon.engagement { background: linear-gradient(135deg, #06b6d4, #22d3ee); }

.metric-content h4 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
}

.metric-content p {
    color: #64748b;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.metric-trend {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
}

.metric-trend.up {
    background: #d1fae5;
    color: #065f46;
}

/* Responsive */
@media (max-width: 768px) {
    .admin-report {
        padding: 1rem 0;
    }
    
    .report-title {
        font-size: 1.75rem;
    }
    
    .header-actions {
        flex-direction: column;
        align-items: stretch;
        margin-top: 1rem;
    }
    
    .chart-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .chart-actions {
        align-self: flex-start;
    }
    
    .stat-card {
        padding: 1.5rem;
    }
    
    .stat-icon {
        width: 50px;
        height: 50px;
        font-size: 1.25rem;
    }
    
    .stat-value {
        font-size: 1.75rem;
    }
}
</style>
