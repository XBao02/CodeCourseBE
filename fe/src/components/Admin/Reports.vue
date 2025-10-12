<template>
    <div class="admin-report container py-4">
        <h2 class="mb-4">📊 Báo cáo thống kê hệ thống</h2>

        <!-- Tab Navigation -->
        <div class="nav nav-tabs mb-4" role="tablist">
            <button 
                class="nav-link"
                :class="{ active: activeTab === 'overview' }"
                @click="activeTab = 'overview'"
                type="button"
            >
                📊 Tổng quan
            </button>
            <button 
                class="nav-link"
                :class="{ active: activeTab === 'courses' }"
                @click="activeTab = 'courses'"
                type="button"
            >
                📚 Khóa học
            </button>
            <button 
                class="nav-link"
                :class="{ active: activeTab === 'revenue' }"
                @click="activeTab = 'revenue'"
                type="button"
            >
                💰 Doanh thu
            </button>
        </div>

        <!-- Tab Overview -->
        <div v-if="activeTab === 'overview'" class="tab-content">
            <!-- Loading indicator -->
            <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tải thống kê tổng quan...</p>
            </div>

            <div v-else>
                <!-- Thống kê tổng quan -->
                <div class="row mb-4">
                    <div class="col-md-3" v-for="stat in stats" :key="stat.title">
                        <div class="card shadow-sm text-center p-3">
                            <h5>{{ stat.title }}</h5>
                            <h3 class="text-primary">{{ stat.value }}</h3>
                        </div>
                    </div>
                </div>

                <!-- Biểu đồ tổng quan -->
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
                </div>
            </div>
        </div>

        <!-- Tab Courses -->
        <div v-if="activeTab === 'courses'" class="tab-content">
            <!-- Loading indicator -->
            <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tải thống kê khóa học...</p>
            </div>

            <div v-else>
                <!-- Thống kê khóa học -->
                <div class="row mb-4">
                    <div class="col-md-4" v-for="stat in courseStats" :key="stat.title">
                        <div class="card shadow-sm text-center p-3">
                            <h5>{{ stat.title }}</h5>
                            <h3 class="text-success">{{ stat.value }}</h3>
                        </div>
                    </div>
                </div>

                <!-- Biểu đồ và bảng khóa học -->
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">Tỉ lệ hoàn thành khóa học</h6>
                            <canvas id="completionChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">Đánh giá khóa học theo sao</h6>
                            <canvas id="ratingChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Bảng khóa học được đánh giá cao -->
                <div class="row">
                    <div class="col-12 mb-4">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">🏆 Top khóa học được đánh giá cao nhất</h6>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Tên khóa học</th>
                                            <th>Giảng viên</th>
                                            <th>Đánh giá</th>
                                            <th>Số học viên</th>
                                            <th>Tỉ lệ hoàn thành</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(course, index) in topCourses" :key="course.id">
                                            <td>{{ index + 1 }}</td>
                                            <td>{{ course.name }}</td>
                                            <td>{{ course.instructor }}</td>
                                            <td>
                                                <span class="badge bg-warning">
                                                    ⭐ {{ course.rating }}/5
                                                </span>
                                            </td>
                                            <td>{{ course.students }}</td>
                                            <td>
                                                <div class="progress" style="height: 20px;">
                                                    <div 
                                                        class="progress-bar bg-success" 
                                                        :style="{ width: course.completion + '%' }"
                                                    >
                                                        {{ course.completion }}%
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab Revenue -->
        <div v-if="activeTab === 'revenue'" class="tab-content">
            <!-- Loading indicator -->
            <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-2">Đang tải dữ liệu doanh thu...</p>
            </div>

            <div v-else>
                <!-- Bộ lọc thời gian và export -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">Chọn khoảng thời gian báo cáo</h6>
                            <div class="btn-group" role="group">
                                <button 
                                    type="button" 
                                    class="btn"
                                    :class="revenueFilter === 'month' ? 'btn-primary' : 'btn-outline-primary'"
                                    @click="changeRevenueFilter('month')"
                                >
                                    Theo tháng
                                </button>
                                <button 
                                    type="button" 
                                    class="btn"
                                    :class="revenueFilter === 'quarter' ? 'btn-primary' : 'btn-outline-primary'"
                                    @click="changeRevenueFilter('quarter')"
                                >
                                    Theo quý
                                </button>
                                <button 
                                    type="button" 
                                    class="btn"
                                    :class="revenueFilter === 'year' ? 'btn-primary' : 'btn-outline-primary'"
                                    @click="changeRevenueFilter('year')"
                                >
                                    Theo năm
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="row">
                            <div class="col-8">
                                <div class="card shadow-sm text-center p-3">
                                    <h5>💰 Tổng doanh thu {{ getRevenueTitle() }}</h5>
                                    <h3 class="text-success">{{ formatCurrency(getTotalRevenue()) }}</h3>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card shadow-sm p-3">
                                    <h6 class="mb-2">📊 Export</h6>
                                    <button class="btn btn-success btn-sm mb-1 w-100" @click="exportReport('excel')">
                                        📄 Excel
                                    </button>
                                    <button class="btn btn-danger btn-sm w-100" @click="exportReport('pdf')">
                                        📋 PDF
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Biểu đồ doanh thu -->
                <div class="row">
                    <div class="col-md-12 mb-4">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">Biểu đồ doanh thu {{ getRevenueTitle() }}</h6>
                            <canvas id="revenueChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Bảng chi tiết doanh thu -->
                <div class="row">
                    <div class="col-12 mb-4">
                        <div class="card p-3 shadow-sm">
                            <h6 class="mb-3">📋 Chi tiết doanh thu {{ getRevenueTitle() }}</h6>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Kỳ</th>
                                            <th>Doanh thu</th>
                                            <th>Số đơn hàng</th>
                                            <th>Trung bình/đơn</th>
                                            <th>Tăng trưởng</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(item, index) in getRevenueTableData()" :key="index">
                                            <td>{{ item.period }}</td>
                                            <td class="fw-bold">{{ formatCurrency(item.revenue) }}</td>
                                            <td>{{ item.orders }}</td>
                                            <td>{{ formatCurrency(item.average) }}</td>
                                            <td>
                                                <span 
                                                    class="badge"
                                                    :class="item.growth >= 0 ? 'bg-success' : 'bg-danger'"
                                                >
                                                    {{ item.growth >= 0 ? '+' : '' }}{{ item.growth }}%
                                                </span>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { onMounted, ref, watch } from "vue";
import Chart from "chart.js/auto";
import reportService from "../../services/reportService";

export default {
    name: "AdminReport",
    setup() {
        const activeTab = ref('overview');
        const loading = ref(false);
        
        const stats = ref([
            { title: "👥 Người dùng", value: 1520 },
            { title: "📚 Khóa học", value: 230 },
            { title: "💰 Doanh thu (VNĐ)", value: "120,000,000" },
            { title: "📊 Hoàn thành TB", value: "78%" }
        ]);

        const courseStats = ref([
            { title: "📚 Tổng khóa học", value: 230 },
            { title: "✅ Khóa học hoàn thành", value: 180 },
            { title: "⭐ Đánh giá TB", value: "4.6/5" }
        ]);

        const topCourses = ref([]);
        const revenueFilter = ref('month');
        const revenueData = ref({});
        let charts = {};

        // Load data functions
        const loadOverviewData = async () => {
            try {
                loading.value = true;
                
                const [overviewRes, studentsRes, userRatioRes] = await Promise.all([
                    reportService.getOverviewStats(),
                    reportService.getStudentsByMonth(),
                    reportService.getUserRatio()
                ]);

                if (overviewRes.success) {
                    const data = overviewRes.data;
                    stats.value = [
                        { title: "👥 Người dùng", value: data.totalUsers.toLocaleString() },
                        { title: "📚 Khóa học", value: data.totalCourses },
                        { title: "💰 Doanh thu (VNĐ)", value: reportService.formatCurrency(data.totalRevenue) },
                        { title: "📊 Hoàn thành TB", value: `${data.averageCompletion}%` }
                    ];
                }
            } catch (error) {
                console.error('Error loading overview data:', error);
            } finally {
                loading.value = false;
            }
        };

        const loadCourseData = async () => {
            try {
                loading.value = true;

                const [courseStatsRes, topCoursesRes, ratingsRes] = await Promise.all([
                    reportService.getCourseStats(),
                    reportService.getTopRatedCourses(5),
                    reportService.getCourseRatings()
                ]);

                if (courseStatsRes.success) {
                    const data = courseStatsRes.data;
                    courseStats.value = [
                        { title: "📚 Tổng khóa học", value: data.total },
                        { title: "✅ Khóa học hoàn thành", value: data.completed },
                        { title: "⭐ Đánh giá TB", value: `${data.averageRating}/5` }
                    ];
                }

                if (topCoursesRes.success) {
                    topCourses.value = topCoursesRes.data;
                }
            } catch (error) {
                console.error('Error loading course data:', error);
            } finally {
                loading.value = false;
            }
        };

        const loadRevenueData = async () => {
            try {
                loading.value = true;
                const response = await reportService.getRevenueData(revenueFilter.value);
                
                if (response.success) {
                    revenueData.value = response.data;
                }
            } catch (error) {
                console.error('Error loading revenue data:', error);
            } finally {
                loading.value = false;
            }
        };

        const initCharts = () => {
            // Destroy existing charts
            Object.values(charts).forEach(chart => {
                if (chart) chart.destroy();
            });
            charts = {};

            // Overview charts
            if (activeTab.value === 'overview') {
                setTimeout(() => {
                    const studentChartElement = document.getElementById("studentChart");
                    const userPieChartElement = document.getElementById("userPieChart");
                    
                    if (studentChartElement) {
                        charts.student = new Chart(studentChartElement, {
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
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: 'top',
                                    }
                                }
                            }
                        });
                    }

                    if (userPieChartElement) {
                        charts.userPie = new Chart(userPieChartElement, {
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
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                    }
                                }
                            }
                        });
                    }
                }, 100);
            }

            // Course charts
            if (activeTab.value === 'courses') {
                setTimeout(() => {
                    const completionChartElement = document.getElementById("completionChart");
                    const ratingChartElement = document.getElementById("ratingChart");
                    
                    if (completionChartElement) {
                        charts.completion = new Chart(completionChartElement, {
                            type: "doughnut",
                            data: {
                                labels: ["Hoàn thành", "Chưa hoàn thành", "Đang học"],
                                datasets: [
                                    {
                                        data: [78, 12, 10],
                                        backgroundColor: ["#4CAF50", "#F44336", "#FF9800"],
                                    },
                                ],
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                    }
                                }
                            }
                        });
                    }

                    if (ratingChartElement) {
                        charts.rating = new Chart(ratingChartElement, {
                            type: "bar",
                            data: {
                                labels: ["5 sao", "4 sao", "3 sao", "2 sao", "1 sao"],
                                datasets: [
                                    {
                                        label: "Số lượng đánh giá",
                                        data: [145, 89, 34, 12, 5],
                                        backgroundColor: [
                                            "#4CAF50",
                                            "#8BC34A", 
                                            "#FFEB3B",
                                            "#FF9800",
                                            "#F44336"
                                        ],
                                    },
                                ],
                            },
                            options: {
                                responsive: true,
                                plugins: {
                                    legend: {
                                        display: false
                                    }
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true
                                    }
                                }
                            }
                        });
                    }
                }, 100);
            }

            // Revenue chart
            if (activeTab.value === 'revenue') {
                updateRevenueChart();
            }
        };

        const updateRevenueChart = () => {
            setTimeout(() => {
                if (charts.revenue) {
                    charts.revenue.destroy();
                }

                const revenueChartElement = document.getElementById("revenueChart");
                if (revenueChartElement && revenueData.value.labels) {
                    charts.revenue = new Chart(revenueChartElement, {
                        type: "line",
                        data: {
                            labels: revenueData.value.labels,
                            datasets: [
                                {
                                    label: "Doanh thu (VNĐ)",
                                    data: revenueData.value.data,
                                    borderColor: "#EF5350",
                                    backgroundColor: "rgba(239, 83, 80, 0.1)",
                                    fill: true,
                                    tension: 0.4
                                },
                            ],
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        callback: function(value) {
                                            return formatCurrency(value);
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            }, 100);
        };

        const changeRevenueFilter = async (filter) => {
            revenueFilter.value = filter;
            await loadRevenueData();
            if (activeTab.value === 'revenue') {
                updateRevenueChart();
            }
        };

        const formatCurrency = (amount) => {
            return reportService.formatCurrency(amount);
        };

        const getRevenueTitle = () => {
            const titles = {
                month: 'theo tháng',
                quarter: 'theo quý', 
                year: 'theo năm'
            };
            return titles[revenueFilter.value];
        };

        const getTotalRevenue = () => {
            if (!revenueData.value.data) return 0;
            return revenueData.value.data.reduce((sum, value) => sum + value, 0);
        };

        const getRevenueTableData = () => {
            return revenueData.value.details || [];
        };

        // Watch for tab changes
        watch(activeTab, async (newTab) => {
            switch (newTab) {
                case 'overview':
                    await loadOverviewData();
                    break;
                case 'courses':
                    await loadCourseData();
                    break;
                case 'revenue':
                    await loadRevenueData();
                    break;
            }
            setTimeout(initCharts, 100);
        });

        onMounted(async () => {
            await loadOverviewData();
            setTimeout(initCharts, 100);
        });

        const exportReport = async (format) => {
            try {
                loading.value = true;
                const response = await reportService.exportReport(format, revenueFilter.value);
                
                if (response.success) {
                    // Simulate download
                    const link = document.createElement('a');
                    link.href = response.data.downloadUrl;
                    link.download = response.data.filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Show success message (if you have a toast system)
                    console.log(`Đã export báo cáo ${format.toUpperCase()}: ${response.data.filename}`);
                }
            } catch (error) {
                console.error('Error exporting report:', error);
            } finally {
                loading.value = false;
            }
        };

        return { 
            activeTab,
            loading,
            stats,
            courseStats,
            topCourses,
            revenueFilter,
            revenueData,
            changeRevenueFilter,
            formatCurrency,
            getRevenueTitle,
            getTotalRevenue,
            getRevenueTableData,
            exportReport
        };
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

.nav-tabs .nav-link {
    border-radius: 8px 8px 0 0;
}

.nav-tabs .nav-link.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
}

.progress {
    border-radius: 10px;
}

.table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.btn-group .btn {
    border-radius: 0;
}

.btn-group .btn:first-child {
    border-radius: 6px 0 0 6px;
}

.btn-group .btn:last-child {
    border-radius: 0 6px 6px 0;
}

.badge {
    font-size: 0.8em;
}
</style>
