/**
 * Service quản lý báo cáo và thống kê cho Admin
 */

// Mock data cho các báo cáo
const mockData = {
    // Thống kê tổng quan
    overview: {
        totalUsers: 1520,
        totalCourses: 230,
        totalRevenue: 423000000,
        averageCompletion: 78
    },

    // Dữ liệu học viên theo tháng
    studentsByMonth: [
        { month: 'Th1', students: 120, active: 89 },
        { month: 'Th2', students: 150, active: 112 },
        { month: 'Th3', students: 200, active: 156 },
        { month: 'Th4', students: 180, active: 134 },
        { month: 'Th5', students: 220, active: 167 },
        { month: 'Th6', students: 300, active: 234 }
    ],

    // Tỉ lệ user types
    userRatio: {
        students: 1300,
        instructors: 220
    },

    // Thống kê khóa học
    courseStats: {
        total: 230,
        completed: 180,
        averageRating: 4.6,
        completionRate: {
            completed: 78,
            inProgress: 12,
            notStarted: 10
        }
    },

    // Top khóa học được đánh giá cao
    topRatedCourses: [
        {
            id: 1,
            name: "JavaScript Fundamentals",
            instructor: "Nguyễn Văn A",
            rating: 4.9,
            students: 1250,
            completion: 85,
            revenue: 15000000
        },
        {
            id: 2,
            name: "React Advanced",
            instructor: "Trần Thị B",
            rating: 4.8,
            students: 980,
            completion: 78,
            revenue: 12500000
        },
        {
            id: 3,
            name: "Python for Data Science",
            instructor: "Lê Văn C",
            rating: 4.7,
            students: 756,
            completion: 82,
            revenue: 11200000
        },
        {
            id: 4,
            name: "Node.js Backend",
            instructor: "Phạm Thị D",
            rating: 4.6,
            students: 634,
            completion: 75,
            revenue: 9800000
        },
        {
            id: 5,
            name: "Vue.js Complete Guide",
            instructor: "Hoàng Văn E",
            rating: 4.5,
            students: 523,
            completion: 80,
            revenue: 8500000
        }
    ],

    // Dữ liệu doanh thu
    revenue: {
        monthly: {
            labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
            data: [15000000, 20000000, 25000000, 18000000, 30000000, 35000000, 32000000, 28000000, 33000000, 38000000, 42000000, 45000000],
            orders: [45, 67, 78, 56, 89, 95, 87, 76, 91, 103, 115, 128],
            details: [
                { period: 'Tháng 1/2024', revenue: 15000000, orders: 45, average: 333333, growth: 0 },
                { period: 'Tháng 2/2024', revenue: 20000000, orders: 67, average: 298507, growth: 33.3 },
                { period: 'Tháng 3/2024', revenue: 25000000, orders: 78, average: 320513, growth: 25.0 },
                { period: 'Tháng 4/2024', revenue: 18000000, orders: 56, average: 321429, growth: -28.0 },
                { period: 'Tháng 5/2024', revenue: 30000000, orders: 89, average: 337079, growth: 66.7 },
                { period: 'Tháng 6/2024', revenue: 35000000, orders: 95, average: 368421, growth: 16.7 }
            ]
        },
        quarterly: {
            labels: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024', 'Q2 2024'],
            data: [60000000, 83000000, 93000000, 119000000, 98000000, 125000000],
            orders: [190, 251, 254, 324, 267, 339],
            details: [
                { period: 'Q1/2023', revenue: 60000000, orders: 190, average: 315789, growth: 0 },
                { period: 'Q2/2023', revenue: 83000000, orders: 251, average: 330677, growth: 38.3 },
                { period: 'Q3/2023', revenue: 93000000, orders: 254, average: 366142, growth: 12.0 },
                { period: 'Q4/2023', revenue: 119000000, orders: 324, average: 367284, growth: 28.0 },
                { period: 'Q1/2024', revenue: 98000000, orders: 267, average: 367042, growth: -17.6 },
                { period: 'Q2/2024', revenue: 125000000, orders: 339, average: 368729, growth: 27.6 }
            ]
        },
        yearly: {
            labels: ['2020', '2021', '2022', '2023', '2024'],
            data: [180000000, 245000000, 298000000, 355000000, 423000000],
            orders: [567, 789, 923, 1019, 1205],
            details: [
                { period: '2020', revenue: 180000000, orders: 567, average: 317460, growth: 0 },
                { period: '2021', revenue: 245000000, orders: 789, average: 310519, growth: 36.1 },
                { period: '2022', revenue: 298000000, orders: 923, average: 322862, growth: 21.6 },
                { period: '2023', revenue: 355000000, orders: 1019, average: 348381, growth: 19.1 },
                { period: '2024', revenue: 423000000, orders: 1205, average: 351037, growth: 19.2 }
            ]
        }
    },

    // Đánh giá khóa học
    courseRatings: {
        distribution: [
            { stars: 5, count: 145, percentage: 55.2 },
            { stars: 4, count: 89, percentage: 33.8 },
            { stars: 3, count: 34, percentage: 12.9 },
            { stars: 2, count: 12, percentage: 4.6 },
            { stars: 1, count: 5, percentage: 1.9 }
        ]
    }
};

class ReportService {
    constructor() {
        this.baseURL = '/api/admin/reports';
    }

    /**
     * Lấy thống kê tổng quan
     */
    async getOverviewStats() {
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));
            return {
                success: true,
                data: mockData.overview
            };
        } catch (error) {
            console.error('Error fetching overview stats:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy dữ liệu học viên theo tháng
     */
    async getStudentsByMonth() {
        try {
            await new Promise(resolve => setTimeout(resolve, 300));
            return {
                success: true,
                data: mockData.studentsByMonth
            };
        } catch (error) {
            console.error('Error fetching students by month:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy tỉ lệ user types
     */
    async getUserRatio() {
        try {
            await new Promise(resolve => setTimeout(resolve, 200));
            return {
                success: true,
                data: mockData.userRatio
            };
        } catch (error) {
            console.error('Error fetching user ratio:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy thống kê khóa học
     */
    async getCourseStats() {
        try {
            await new Promise(resolve => setTimeout(resolve, 400));
            return {
                success: true,
                data: mockData.courseStats
            };
        } catch (error) {
            console.error('Error fetching course stats:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy top khóa học được đánh giá cao
     */
    async getTopRatedCourses(limit = 10) {
        try {
            await new Promise(resolve => setTimeout(resolve, 300));
            const courses = mockData.topRatedCourses.slice(0, limit);
            return {
                success: true,
                data: courses
            };
        } catch (error) {
            console.error('Error fetching top rated courses:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy dữ liệu doanh thu theo kỳ
     */
    async getRevenueData(period = 'monthly') {
        try {
            await new Promise(resolve => setTimeout(resolve, 400));
            
            const periodMap = {
                'month': 'monthly',
                'quarter': 'quarterly', 
                'year': 'yearly'
            };
            
            const mappedPeriod = periodMap[period] || period;
            const data = mockData.revenue[mappedPeriod];
            
            if (!data) {
                throw new Error(`Invalid period: ${period}`);
            }

            return {
                success: true,
                data: data
            };
        } catch (error) {
            console.error('Error fetching revenue data:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy phân bố đánh giá khóa học
     */
    async getCourseRatings() {
        try {
            await new Promise(resolve => setTimeout(resolve, 200));
            return {
                success: true,
                data: mockData.courseRatings
            };
        } catch (error) {
            console.error('Error fetching course ratings:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lấy báo cáo chi tiết theo tháng
     */
    async getMonthlyReport(year = new Date().getFullYear(), month = new Date().getMonth() + 1) {
        try {
            await new Promise(resolve => setTimeout(resolve, 600));
            
            // Tạo dữ liệu báo cáo chi tiết cho tháng cụ thể
            const report = {
                period: `${month}/${year}`,
                summary: {
                    newStudents: 300,
                    newCourses: 15,
                    revenue: 35000000,
                    completionRate: 78
                },
                topCourses: mockData.topRatedCourses.slice(0, 5),
                trends: {
                    studentsGrowth: 12.5,
                    revenueGrowth: 16.7,
                    satisfactionScore: 4.6
                }
            };

            return {
                success: true,
                data: report
            };
        } catch (error) {
            console.error('Error fetching monthly report:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Export báo cáo ra file Excel/PDF
     */
    async exportReport(type = 'excel', period = 'monthly', startDate, endDate) {
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Simulate file generation
            const filename = `report_${period}_${Date.now()}.${type === 'excel' ? 'xlsx' : 'pdf'}`;
            
            return {
                success: true,
                data: {
                    filename,
                    downloadUrl: `/api/reports/download/${filename}`,
                    size: '2.5MB'
                }
            };
        } catch (error) {
            console.error('Error exporting report:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Utility: Format tiền tệ
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    }

    /**
     * Utility: Tính phần trăm tăng trưởng
     */
    calculateGrowth(current, previous) {
        if (previous === 0) return 0;
        return ((current - previous) / previous * 100).toFixed(1);
    }

    /**
     * Utility: Lấy màu cho biểu đồ
     */
    getChartColors() {
        return {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            light: '#f8f9fa',
            dark: '#343a40'
        };
    }
}

export default new ReportService();
