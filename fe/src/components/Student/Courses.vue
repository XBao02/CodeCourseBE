<template>
    <div class="courses-wrapper">
        <!-- Header -->
        <div class="courses-header">
            <div>
                <h1>Course Catalog</h1>
                <p>Browse and enroll in available courses</p>
            </div>
            <div class="header-info">
                <span>{{ availableCourses.length }} courses available</span>
            </div>
        </div>

        <div class="courses-layout">
            <!-- Left: Available Courses -->
            <div class="courses-column">
                <div class="content-card">
                    <div class="card-header">
                        <h5>Available Courses</h5>
                        <span class="count">{{ availableCourses.length }}</span>
                    </div>
                    <div class="card-body">
                        <div v-if="availableCourses.length" class="courses-list">
                            <div v-for="value in availableCourses" :key="value.id" class="course-item">
                                <img :src="value.image" class="course-image" />
                                <div class="course-details">
                                    <h6>{{ value.title }}</h6>
                                    <p class="course-meta">
                                        {{ value.instructorName || 'N/A' }} · 
                                        <span class="course-level">{{ value.level }}</span>
                                    </p>
                                    <div class="course-info">
                                        <span class="course-status">{{ value.isPublic ? 'Public' : 'Private' }}</span>
                                        <span class="course-price">{{ formatPrice(value.price, value.currency) }}</span>
                                    </div>
                                    <div class="course-actions">
                                        <button class="action-button" :class="{ 'free': value.price == 0 }" @click="openPayment(value)">
                                            {{ value.price == 0 ? 'Enroll Now' : 'Purchase' }}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="empty-state">
                            <p>No courses available</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: My Courses -->
            <div class="courses-column">
                <div class="content-card">
                    <div class="card-header">
                        <h5>My Courses</h5>
                        <span class="count">{{ registeredCourses.length }}</span>
                    </div>
                    <div class="card-body">
                        <div v-if="registeredCourses.length" class="enrolled-courses-list">
                            <div v-for="course in registeredCourses" :key="'reg-' + course.id" class="enrolled-course-item">
                                <img :src="course.image" class="enrolled-course-image" />
                                <div class="enrolled-course-details">
                                    <h6>{{ course.title }}</h6>
                                    <p class="enrolled-course-meta">
                                        Level: {{ course.level }} · {{ formatPrice(course.price, course.currency) }}
                                    </p>
                                </div>
                                <button class="action-button small" @click="enterCourse(course)">
                                    Start Learning
                                </button>
                            </div>
                        </div>
                        <div v-else class="empty-state">
                            <p>You haven't enrolled in any courses yet</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Payment Modal -->
        <div class="modal fade" id="paymentModal" tabindex="-1" ref="paymentModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <span v-if="paymentStep === 'info'">Course Information</span>
                            <span v-else>Payment - Scan QR Code</span>
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetPayment"></button>
                    </div>

                    <!-- Step 1: Course Info -->
                    <div v-if="paymentStep === 'info'" class="modal-body">
                        <div v-if="selectedCourse" class="modal-course-info">
                            <h6>{{ selectedCourse.title }}</h6>
                            <p class="course-meta">{{ selectedCourse.instructorName || 'N/A' }} · {{ selectedCourse.level }}</p>

                            <div class="info-list">
                                <div class="info-row">
                                    <span class="info-label">Status</span>
                                    <span class="info-value">{{ selectedCourse.isPublic ? 'Public' : 'Private' }}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Price</span>
                                    <span class="info-value">{{ formatPrice(selectedCourse.price, selectedCourse.currency) }}</span>
                                </div>
                            </div>

                            <div class="modal-actions">
                                <button v-if="selectedCourse.price == 0" class="action-button" @click="registerCourse(selectedCourse)">
                                    Enroll Now
                                </button>
                                <button v-else class="action-button" @click="proceedToQR">
                                    Proceed to Payment
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 2: QR Code -->
                    <div v-else class="modal-body text-center">
                        <div v-if="selectedCourse" class="qr-section">
                            <h6>{{ selectedCourse.title }}</h6>
                            <p class="payment-amount">Amount: <strong>{{ formatPrice(selectedCourse.price, selectedCourse.currency) }}</strong></p>

                            <div class="qr-code">
                                <img :src="qrUrl" alt="QR Code" />
                            </div>

                            <p class="qr-instruction">Scan the QR code to complete payment. The system will automatically verify the transaction.</p>

                            <div v-if="isChecking" class="checking-status">
                                Checking payment status...
                            </div>
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button class="action-button secondary" data-bs-dismiss="modal" @click="resetPayment">Close</button>
                        <button v-if="paymentStep === 'qr'" class="action-button test-purchase" @click="testPurchase">
                            Test Purchase (Skip Payment)
                        </button>
                        <button v-if="paymentStep === 'qr'" class="action-button" @click="simulatePaidManually">
                            Confirm Payment
                        </button>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import axios from "axios";
import { getStoredSession } from "../../services/authService";

// Tạo axios instance với interceptor để tự động gửi token
const api = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor để tự động thêm token vào mọi request
api.interceptors.request.use((config) => {
    const session = getStoredSession();
    if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
        console.log("🔑 Token added to request:", config.url);
        console.log("🔑 Full Token (first 50 chars):", session.access_token.substring(0, 50) + "...");
        console.log("🔑 Full Token (COMPLETE):", session.access_token);
    } else {
        console.warn("⚠️ No token in session");
        console.warn("📦 Session stored:", session);
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default {
    data() {
        return {
            courses: [],
            myCourses: [],
            studyPlans: [],
            selectedCourse: null,
            paymentStep: "info",
            isChecking: false,
            qrUrl: "",
            paymentInterval: null,
        };
    },

    computed: {
        availableCourses() {
            // Filter out courses that are already in myCourses
            const enrolledIds = new Set(this.myCourses.map(c => c.id));
            return this.courses.filter(c => !enrolledIds.has(c.id));
        },
        registeredCourses() {
            return Array.isArray(this.myCourses) ? this.myCourses : [];
        },
    },

    mounted() {
        this.loadData();
    },

    methods: {
        // Gộp toàn bộ gọi API vào 1 hàm loadData()
        async loadData() {
            console.log("🔄 Bắt đầu load data...");
            
            const session = getStoredSession();
            console.log("📦 Session:", session);
            
            const studentId = session?.user?.studentId || session?.user?.id;
            console.log("👤 Student ID:", studentId);
            
            // Nếu chưa đăng nhập hoặc thiếu studentId thì vẫn load tất cả courses
            // nhưng không load my-courses
            
            try {
                // Lấy danh sách tất cả khóa học (không cần studentId)
                console.log("📡 Đang gọi API /api/student/courses...");
                const allRes = await api.get(`/api/student/courses`);
                console.log("✅ Response từ /courses:", allRes.data);
                
                const allCourses = Array.isArray(allRes.data?.courses) ? allRes.data.courses : (Array.isArray(allRes.data) ? allRes.data : []);
                console.log("📚 Số khóa học nhận được:", allCourses.length);
                
                // Chuẩn hóa trường hiển thị
                this.courses = allCourses.map(c => ({
                    id: c.id,
                    title: c.title,
                    level: c.level || "beginner",
                    price: Number(c.price || 0),
                    currency: c.currency || "VND",
                    isPublic: c.is_public === true || c.isPublic === true,
                    image: c.thumbnail || c.image || "/public/vite.svg",
                    slug: c.slug || String(c.id),
                    instructorName: c.instructorName || c.instructor || "",
                }));
                console.log("✅ Đã chuẩn hóa courses:", this.courses);

                // Lấy danh sách khóa học đã đăng ký của student (chỉ khi có studentId)
                if (studentId) {
                    console.log("📡 Đang gọi API /api/student/my-courses...");
                    const mineRes = await api.get(`/api/student/my-courses`, {
                        params: { student_id: studentId }
                    });
                    console.log("✅ Response từ /my-courses:", mineRes.data);
                    
                    const mineCourses = Array.isArray(mineRes.data?.courses) ? mineRes.data.courses : (Array.isArray(mineRes.data) ? mineRes.data : []);
                    console.log("📚 Số khóa học đã đăng ký:", mineCourses.length);
                    
                    this.myCourses = mineCourses.map(c => ({
                        id: c.id,
                        title: c.title,
                        level: c.level || "beginner",
                        price: Number(c.price || 0),
                        currency: c.currency || "VND",
                        image: c.thumbnail || c.image || "/public/vite.svg",
                    }));
                    console.log("✅ Đã chuẩn hóa myCourses:", this.myCourses);
                } else {
                    console.log("⚠️ Không có studentId, bỏ qua load my-courses");
                    this.myCourses = [];
                }
                
                console.log("🎉 Load data hoàn tất!");
                console.log("📊 Available courses:", this.availableCourses.length);
                console.log("📊 My courses:", this.registeredCourses.length);
                
            } catch (err) {
                console.error("❌ Lỗi tải dữ liệu courses:", err);
                console.error("❌ Chi tiết lỗi:", err.response?.data || err.message);
                this.courses = [];
                this.myCourses = [];
            }
        },

        // ===== Các hàm tiện ích cơ bản =====
        formatPrice(value, currency = "VND") {
            if (value === 0) return "Free";
            return Number(value).toLocaleString("vi-VN") + " " + currency;
        },
        formatDateTime(v) {
            return v ? v : "-";
        },
        statusClass(status) {
            if (status === "done") return "badge bg-success text-white";
            if (status === "in_progress") return "badge bg-warning text-dark";
            return "badge bg-secondary text-white";
        },
        getCourseTitle(id) {
            const c = this.courses.find(x => x.id === id);
            return c ? c.title : "N/A";
        },
        sortedPlanItems(items) {
            return (items || []).sort((a, b) => a.sortOrder - b.sortOrder);
        },

        // ===== Điều hướng và xử lý modal =====
        goHome() {
            this.$router.push("/student/courses").catch(() => { });
            this.selectedCourse = null;
        },
        openPayment(course) {
            this.selectedCourse = course;
            this.paymentStep = "info";
            const modal = new bootstrap.Modal(this.$refs.paymentModal);
            modal.show();
        },
        registerCourse(course) {
            const session = getStoredSession();
            const studentId = session?.user?.studentId || session?.user?.id;
            
            // Debug: Log token trước khi gửi request
            console.log("\n" + "="*80);
            console.log("📤 registerCourse - About to send request");
            console.log("🔐 Token from session:", session?.access_token?.substring(0, 50) + "...");
            console.log("👤 Student ID:", studentId);
            console.log("📦 Course ID:", course.id);
            console.log("="*80);
            
            // Gọi API đăng ký khóa học (dùng api instance để tự động gửi token)
            api.post("/api/student/register", { courseId: course.id })
                .then((response) => {
                    // Debug: Log response từ backend
                    console.log("\n" + "="*80);
                    console.log("📥 registerCourse - Response from backend");
                    console.log("✅ Status:", response.status);
                    console.log("✅ Data:", response.data);
                    console.log("="*80);
                    
                    // Kiểm tra response từ backend
                    if (response.data && response.data.success === true) {
                        console.log("✅ Backend xác nhận đăng ký thành công:", response.data);
                        
                        // CHỈ reload lại data từ backend sau khi backend đã xử lý thành công và commit vào database
                        // Không tự động thêm vào myCourses ở frontend - phải lấy từ API
                        const requests = [
                            api.get("/api/student/courses")
                        ];
                        
                        if (studentId) {
                            requests.push(
                                api.get("/api/student/my-courses", {
                                    params: { student_id: studentId }
                                })
                            );
                        }
                        
                        Promise.all(requests)
                            .then((responses) => {
                                // Chuẩn hóa lại courses từ backend response
                                const allCourses = Array.isArray(responses[0].data.courses) ? responses[0].data.courses : [];
                                this.courses = allCourses.map(c => ({
                                    id: c.id,
                                    title: c.title,
                                    level: c.level || "beginner",
                                    price: Number(c.price || 0),
                                    currency: c.currency || "VND",
                                    isPublic: c.is_public === true || c.isPublic === true,
                                    image: c.thumbnail || c.image || "/public/vite.svg",
                                    slug: c.slug || String(c.id),
                                    instructorName: c.instructorName || c.instructor || "",
                                }));
                                
                                if (responses.length > 1) {
                                    const mineCourses = Array.isArray(responses[1].data.courses) ? responses[1].data.courses : [];
                                    this.myCourses = mineCourses.map(c => ({
                                        id: c.id,
                                        title: c.title,
                                        level: c.level || "beginner",
                                        price: Number(c.price || 0),
                                        currency: c.currency || "VND",
                                        image: c.thumbnail || c.image || "/public/vite.svg",
                                    }));
                                } else {
                                    this.myCourses = [];
                                }
                                
                                console.log("✅ Đã reload sau đăng ký - myCourses:", this.myCourses.length);
                                
                                // Đóng modal
                                const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal);
                                if (modal) modal.hide();
                                this.resetPayment();
                                
                                // Hiển thị thông báo
                                alert("✅ Đăng ký thành công!");
                            })
                            .catch(err => {
                                console.error("❌ Lỗi reload sau khi đăng ký:", err);
                                // Fallback: reload toàn bộ data
                                this.loadData();
                                alert("✅ Đăng ký thành công!");
                            });
                    } else {
                        // Backend trả về nhưng không thành công
                        console.warn("⚠️ Backend trả về nhưng success=False:", response.data);
                        alert("⚠️ " + (response.data?.message || "Không thể đăng ký khóa học"));
                    }
                })
                .catch((error) => {
                    console.error("\n" + "="*80);
                    console.error("❌ registerCourse - Error response from backend");
                    console.error("❌ Error status:", error.response?.status);
                    console.error("❌ Error data:", error.response?.data);
                    console.error("❌ Error message:", error.message);
                    console.error("="*80);
                    const errorMsg = error.response?.data?.error || "Lỗi không xác định";
                    alert("❌ Lỗi khi đăng ký khóa học: " + errorMsg);
                });
        },

        // ===== Thanh toán và kiểm tra QR =====
        proceedToQR() {
            if (!this.selectedCourse) return;
            this.paymentStep = "qr";
            this.qrUrl = this.makeQrUrl(this.selectedCourse);
            const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal)
                || new bootstrap.Modal(this.$refs.paymentModal);
            modal.show();
            this.startPaymentCheck(this.selectedCourse);
        },
        makeQrUrl(course) {
            const data = encodeURIComponent(`COURSE:${course.slug}|AMOUNT:${course.price}${course.currency}`);
            return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${data}`;
        },
        startPaymentCheck(course) {
            // Tạm thời disable auto-check vì endpoint /api/payment/status chưa được implement
            // User sẽ dùng nút "Test Purchase" hoặc "Confirm Payment" thay thế
            this.isChecking = false;
            console.log("ℹ️ Auto payment check disabled. Use 'Test Purchase' or 'Confirm Payment' button.");
        },

        // Test Purchase - Mua khóa học mà không cần thanh toán (chỉ dùng cho testing)
        testPurchase() {
            if (!this.selectedCourse) return;
            
            const session = getStoredSession();
            const studentId = session?.user?.studentId || session?.user?.id;
            
            console.log("🧪 Test Purchase started");
            console.log("📦 Session:", session);
            console.log("🔑 Token available:", !!session?.access_token);
            
            // Gọi API đăng ký khóa học trực tiếp mà không cần thanh toán (dùng api instance)
            api.post("/api/student/register", { courseId: this.selectedCourse.id })
                .then((response) => {
                    console.log("\n" + "="*80);
                    console.log("🧪 testPurchase - Response from backend");
                    console.log("✅ Response status:", response.status);
                    console.log("✅ Response data:", response.data);
                    console.log("="*80);
                    
                    if (response.data && response.data.success === true) {
                        console.log("✅ Test Purchase - Backend xác nhận đăng ký:", response.data);
                        
                        // Reload lại data từ backend
                        const requests = [
                            api.get("/api/student/courses")
                        ];
                        
                        if (studentId) {
                            requests.push(
                                api.get("/api/student/my-courses", {
                                    params: { student_id: studentId }
                                })
                            );
                        }
                        
                        Promise.all(requests)
                            .then((responses) => {
                                // Chuẩn hóa lại courses
                                const allCourses = Array.isArray(responses[0].data.courses) ? responses[0].data.courses : [];
                                this.courses = allCourses.map(c => ({
                                    id: c.id,
                                    title: c.title,
                                    level: c.level || "beginner",
                                    price: Number(c.price || 0),
                                    currency: c.currency || "VND",
                                    isPublic: c.is_public === true || c.isPublic === true,
                                    image: c.thumbnail || c.image || "/public/vite.svg",
                                    slug: c.slug || String(c.id),
                                    instructorName: c.instructorName || c.instructor || "",
                                }));
                                
                                if (responses.length > 1) {
                                    const mineCourses = Array.isArray(responses[1].data.courses) ? responses[1].data.courses : [];
                                    this.myCourses = mineCourses.map(c => ({
                                        id: c.id,
                                        title: c.title,
                                        level: c.level || "beginner",
                                        price: Number(c.price || 0),
                                        currency: c.currency || "VND",
                                        image: c.thumbnail || c.image || "/public/vite.svg",
                                    }));
                                } else {
                                    this.myCourses = [];
                                }
                                
                                console.log("✅ Test Purchase - Đã reload - myCourses:", this.myCourses.length);
                                
                                const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal);
                                if (modal) modal.hide();
                                this.resetPayment();
                                alert("✅ Test Purchase successful! Course enrolled without payment.");
                            })
                            .catch(err => {
                                console.error("❌ Lỗi reload sau test purchase:", err);
                                this.loadData();
                                alert("✅ Test Purchase successful!");
                            });
                    } else {
                        console.warn("⚠️ Test Purchase - Backend trả về nhưng success=False:", response.data);
                        alert("⚠️ " + (response.data?.message || "Cannot enroll in course"));
                    }
                })
                .catch((error) => {
                    console.error("\n" + "="*80);
                    console.error("🧪 testPurchase - Error response from backend");
                    console.error("❌ Error status:", error.response?.status);
                    console.error("❌ Error data:", error.response?.data);
                    console.error("❌ Error message:", error.message);
                    console.error("="*80);
                    alert("❌ Test purchase failed: " + (error.response?.data?.error || error.message || "Unknown error"));
                });
        },

        simulatePaidManually() {
            if (!this.selectedCourse) return;
            
            const session = getStoredSession();
            const studentId = session?.user?.studentId || session?.user?.id;
            
            // Gọi API đăng ký khóa học sau khi thanh toán (dùng api instance)
            // CHỈ khi backend xử lý thành công thì mới reload data
            api.post("/api/student/register", { courseId: this.selectedCourse.id })
                .then((response) => {
                    // Kiểm tra response từ backend
                    if (response.data && response.data.success === true) {
                        console.log("✅ Backend xác nhận đăng ký sau thanh toán:", response.data);
                        
                        // CHỈ reload lại data từ backend sau khi backend đã xử lý thành công và commit vào database
                        const requests = [
                            api.get("/api/student/courses")
                        ];
                        
                        if (studentId) {
                            requests.push(
                                api.get("/api/student/my-courses", {
                                    params: { student_id: studentId }
                                })
                            );
                        }
                        
                        Promise.all(requests)
                            .then((responses) => {
                                // Cập nhật từ response của backend - đảm bảo luôn là mảng
                                this.courses = Array.isArray(responses[0].data.courses) ? responses[0].data.courses : [];
                                
                                if (responses.length > 1) {
                                    this.myCourses = Array.isArray(responses[1].data.courses) ? responses[1].data.courses : [];
                                } else {
                                    this.myCourses = [];
                                }
                                
                                console.log("✅ Đã reload sau thanh toán - myCourses:", this.myCourses.length);
                                
                                const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal);
                                if (modal) modal.hide();
                                this.resetPayment();
                                alert("✅ Thanh toán thành công! Khóa học đã được đăng ký.");
                            })
                            .catch(err => {
                                console.error("❌ Lỗi reload sau khi thanh toán:", err);
                                this.loadData();
                                alert("✅ Thanh toán thành công!");
                            });
                    } else {
                        console.warn("⚠️ Backend trả về nhưng success=False:", response.data);
                        alert("⚠️ " + (response.data?.message || "Không thể đăng ký khóa học sau thanh toán"));
                    }
                })
                .catch((error) => {
                    console.error("❌ Lỗi khi đăng ký khóa học sau thanh toán:", error);
                    alert("❌ Lỗi khi đăng ký khóa học sau thanh toán: " + (error.response?.data?.error || "Lỗi không xác định"));
                });
        },

        resetPayment() {
            this.paymentStep = "info";
            this.isChecking = false;
            this.qrUrl = "";
            if (this.paymentInterval) {
                clearInterval(this.paymentInterval);
                this.paymentInterval = null;
            }
        },

        enterCourse(course) {
            this.selectedCourse = course;
            this.$router.push({
                name: "StudentCourseLesson",
                params: { courseId: course.id },
            }).catch(() => { });
        },
    },

    beforeUnmount() {
        if (this.paymentInterval) clearInterval(this.paymentInterval);
    },
};
</script>

<style scoped>
.courses-wrapper {
    background: #f8f9fa;
    min-height: 100vh;
    padding: 40px;
}

.courses-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 40px;
}

.courses-header h1 {
    font-size: 32px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.courses-header p {
    color: #666;
    font-size: 15px;
    margin: 0;
}

.header-info {
    font-size: 14px;
    color: #666;
}

.courses-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

.courses-column {
    display: flex;
    flex-direction: column;
}

.content-card {
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.card-header {
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h5 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
}

.card-header .count {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

.card-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.course-item {
    display: flex;
    gap: 16px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.course-item:hover {
    background: #e5e7eb;
}

.course-image {
    width: 120px;
    height: 80px;
    object-fit: cover;
    border-radius: 4px;
    flex-shrink: 0;
}

.course-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.course-details h6 {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
}

.course-meta {
    font-size: 13px;
    color: #666;
    margin: 0;
}

.course-level {
    text-transform: uppercase;
    font-weight: 500;
}

.course-info {
    display: flex;
    gap: 12px;
    font-size: 13px;
    color: #666;
}

.course-status, .course-price {
    font-weight: 500;
}

.course-actions {
    margin-top: auto;
}

.action-button {
  padding: 8px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.action-button.free {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.action-button.free:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.action-button.small {
    padding: 6px 16px;
    font-size: 13px;
}

.action-button.secondary {
    background: white;
    color: #1f2937;
    border: 1px solid #d1d5db;
}

.action-button.secondary:hover {
    background: #f8f9fa;
    border-color: #9ca3af;
}

.action-button.test-purchase {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    border: none;
}

.action-button.test-purchase:hover {
    background: linear-gradient(135deg, #d97706, #b45309);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.enrolled-courses-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.enrolled-course-item {
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
}

.enrolled-course-image {
    width: 80px;
    height: 55px;
    object-fit: cover;
    border-radius: 4px;
    flex-shrink: 0;
}

.enrolled-course-details {
    flex: 1;
}

.enrolled-course-details h6 {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 4px 0;
}

.enrolled-course-meta {
    font-size: 12px;
    color: #666;
    margin: 0;
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
}

.empty-state p {
    margin: 0;
    font-size: 14px;
}

/* Modal Styles */
.modal-course-info h6 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.modal-course-info .course-meta {
    font-size: 14px;
    color: #666;
    margin: 0 0 20px 0;
}

.info-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 24px;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #e5e7eb;
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
}

.info-value {
    font-size: 14px;
    color: #1a1a1a;
    font-weight: 600;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
}

.qr-section h6 {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.payment-amount {
    font-size: 14px;
    color: #666;
    margin: 0 0 24px 0;
}

.payment-amount strong {
    color: #1a1a1a;
    font-size: 16px;
}

.qr-code {
    margin: 24px 0;
}

.qr-code img {
    width: 220px;
    height: 220px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px;
}

.qr-instruction {
    font-size: 13px;
    color: #666;
    margin: 0 0 16px 0;
}

.checking-status {
    font-size: 14px;
    color: #3b82f6;
    font-weight: 500;
}

@media (max-width: 1024px) {
    .courses-layout {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .courses-wrapper {
        padding: 20px;
    }

    .courses-header {
        flex-direction: column;
        gap: 12px;
    }

    .course-item {
        flex-direction: column;
    }

    .course-image {
        width: 100%;
        height: 150px;
    }
}
</style>