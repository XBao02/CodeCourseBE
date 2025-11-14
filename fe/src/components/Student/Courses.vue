<template>
    <div class="container py-4" style="min-height: calc(100vh - 120px);">
        <!-- Breadcrumb card trên đầu -->
        <div class="card mb-4 border-0 shadow-sm rounded-4">
            <div class="card-body d-flex align-items-center justify-content-between">
                <div>
                    <nav aria-label="breadcrumb" class="mb-0">
                        <ol class="breadcrumb mb-0">
                            <li class="breadcrumb-item">
                                <a href="#" @click.prevent="goHome">Home</a>
                            </li>
                        </ol>
                    </nav>
                </div>
                <div class="text-end small text-muted">
                    <div v-if="selectedCourse">Slug: <strong>{{ selectedCourse.slug }}</strong></div>
                    <div v-else>Hiện có <strong>{{ availableCourses.length }}</strong> khóa học</div>
                </div>
            </div>
        </div>

        <div class="row g-4 h-100">
            <!-- Left: danh sách khóa học (chiếm 50%) -->
            <div class="col-md-6 h-100">
                <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
                    <div class="card-header bg-white d-flex align-items-center justify-content-between">
                        <h5 class="mb-0 fw-semibold">📚 Danh sách khóa học</h5>
                        <span class="text-muted small">{{ availableCourses.length }} khóa học</span>
                    </div>
                    <div class="card-body overflow-auto p-3">
                        <div v-if="availableCourses.length" class="list-group">
                            <div v-for="(value, index) in availableCourses" :key="value.id"
                                class="list-group-item mb-3 rounded-3 border-0 shadow-sm hover-scale">
                                <div class="d-flex align-items-center">
                                    <img :src="value.image" class="me-3 rounded object-fit-cover" width="100"
                                        height="70" />
                                    <div class="flex-grow-1">
                                        <h6 class="mb-1 fw-bold text-dark">{{ value.title }}</h6>
                                        <p class="text-muted small mb-1">{{ value.instructorName || 'N/A' }} · <span
                                                class="badge bg-info text-dark text-uppercase">{{ value.level }}</span>
                                        </p>

                                        <div class="small text-muted mb-2">
                                            <span class="me-3">Trạng thái: <strong>{{ value.isPublic ? 'Public' :
                                                'Private' }}</strong></span>
                                            <span>Giá: <strong class="text-primary">{{ formatPrice(value.price,
                                                value.currency) }}</strong></span>
                                        </div>

                                        <div class="d-flex justify-content-between align-items-center">
                                            <div class="text-muted small"><i class="fas fa-link me-1"></i>Slug: {{
                                                value.slug }}</div>
                                            <div class="text-end">
                                                <div v-if="value.price == 0" class="mb-2">
                                                    <button class="btn btn-success btn-sm"
                                                        @click="openPayment(value)"><i
                                                            class="fas fa-check-circle me-1"></i>Đăng ký</button>
                                                </div>
                                                <div v-else>
                                                    <button class="btn btn-outline-primary btn-sm"
                                                        @click="openPayment(value)"><i
                                                            class="fas fa-credit-card me-1"></i>Thanh toán</button>
                                                </div>
                                            </div>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            <i class="fas fa-info-circle me-2"></i>Không có khóa học mới.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: 2 card (mỗi card chiếm 50% chiều cao của cột phải) -->
            <div class="col-md-6 h-100 d-flex flex-column">
                <!-- Card 1: Lộ trình học (hiển thị StudyPlans & PlanItems) -->
                <div class="card border-0 shadow-sm rounded-4 mb-3 h-50 overflow-auto">
                    <!-- <div class="card-header bg-white d-flex align-items-center justify-content-between">
                        <h6 class="mb-0 fw-semibold">🗺️ Lộ trình học</h6>
                        <small class="text-muted">Kế hoạch cho học viên</small>
                    </div>
                    <div class="card-body">
                        <div v-if="studyPlans.length">
                            <div v-for="plan in studyPlans" :key="plan.id" class="mb-3">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <div class="fw-bold">Plan #{{ plan.id }} — created by {{ plan.createdBy }}</div>
                                    <div class="small text-muted">{{ formatDateTime(plan.createdAt) }}</div>
                                </div>

                                <ul class="list-group mb-2">
                                    <li v-for="item in sortedPlanItems(plan.items)" :key="item.id"
                                        class="list-group-item d-flex justify-content-between align-items-start">
                                        <div>
                                            <div class="fw-semibold">{{ getCourseTitle(item.courseId) }}

                                            </div>
                                            <div class="small text-muted">Mục tiêu: {{ item.targetLevel }} ·
                                                Hạn: {{ item.deadline }}</div>
                                        </div>
                                        <div class="text-end small">
                                            <div>Thứ tự: {{ item.sortOrder }}</div>
                                            <div :class="statusClass(item.status)">{{ item.status }}</div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            <i class="fas fa-info-circle me-2"></i>Chưa có lộ trình học.
                        </div>
                    </div> -->
                </div>

                <!-- Card 2: Khóa học đã đăng ký -->
                <div class="card border-0 shadow-sm rounded-4 h-50 overflow-auto">
                    <div class="card-header bg-white d-flex align-items-center justify-content-between">
                        <h6 class="mb-0 fw-semibold">✅ Khóa học của tôi</h6>
                        <span class="text-muted small">{{ registeredCourses.length }}</span>
                    </div>
                    <div class="card-body p-3">
                        <div v-if="registeredCourses.length" class="list-group">
                            <div v-for="course in registeredCourses" :key="'reg-' + course.id"
                                class="list-group-item mb-3 rounded-3 border-0 shadow-sm d-flex align-items-center">
                                <img :src="course.image" class="me-3 rounded object-fit-cover" width="80" height="55" />
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">{{ course.title }}</h6>
                                    <p class="text-muted small mb-1">Level: {{ course.level }} · {{
                                        formatPrice(course.price, course.currency) }}</p>
                                </div>
                                <button class="btn btn-primary btn-sm ms-2" @click="enterCourse(course)"><i
                                        class="fas fa-play me-1"></i>Vào học</button>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            <i class="fas fa-info-circle me-2"></i>Bạn chưa đăng ký khóa học nào.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal thanh toán: 2 bước (info -> qr) -->
        <div class="modal fade" id="paymentModal" tabindex="-1" ref="paymentModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content rounded-4 shadow">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title fw-semibold">
                            <span v-if="paymentStep === 'info'">💳 Thông tin khóa học</span>
                            <span v-else>🔃 Thanh toán - Quét mã</span>
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"
                            @click="resetPayment"></button>
                    </div>

                    <!-- Bước 1: Thông tin khóa học + hành động -->
                    <div v-if="paymentStep === 'info'" class="modal-body">
                        <div v-if="selectedCourse">
                            <h6 class="fw-bold mb-1">{{ selectedCourse.title }}</h6>
                            <p class="text-muted small mb-2">Giảng viên: {{ selectedCourse.instructorName || 'N/A' }} ·
                                Level: {{ selectedCourse.level }}</p>

                            <dl class="row">
                                <dt class="col-sm-4">Slug</dt>
                                <dd class="col-sm-8">{{ selectedCourse.slug }}</dd>

                                <dt class="col-sm-4">Public</dt>
                                <dd class="col-sm-8">{{ selectedCourse.isPublic ? 'Yes' : 'No' }}</dd>

                                <dt class="col-sm-4">Giá</dt>
                                <dd class="col-sm-8">{{ formatPrice(selectedCourse.price, selectedCourse.currency) }}
                                </dd>

                                <dt class="col-sm-4">Tạo</dt>
                                <dd class="col-sm-8">{{ formatDateTime(selectedCourse.createdAt) }}</dd>

                                <dt class="col-sm-4">Cập nhật</dt>
                                <dd class="col-sm-8">{{ formatDateTime(selectedCourse.updatedAt) }}</dd>
                            </dl>

                            <div class="mt-3 d-flex justify-content-end">
                                <button v-if="selectedCourse.price == 0" class="btn btn-success me-2"
                                    @click="registerCourse(selectedCourse)">Đăng ký</button>
                                <button v-else class="btn btn-primary" @click="proceedToQR">Thanh toán</button>
                            </div>
                        </div>
                    </div>

                    <!-- Bước 2: Hiển thị QR + trạng thái kiểm tra thanh toán -->
                    <div v-else class="modal-body text-center">
                        <div v-if="selectedCourse">
                            <h6 class="fw-bold mb-1">{{ selectedCourse.title }}</h6>
                            <p class="text-muted small mb-2">Thanh toán: <strong>{{ formatPrice(selectedCourse.price,
                                selectedCourse.currency) }}</strong></p>

                            <div class="mb-3">
                                <img :src="qrUrl" alt="QR Code" class="rounded shadow-sm border p-2" width="220"
                                    height="220" />
                            </div>

                            <p class="small text-secondary">Quét mã để thanh toán đúng số tiền. Hệ thống sẽ tự động kiểm
                                tra trạng thái.</p>

                            <div v-if="isChecking" class="text-info small mt-2">
                                ⏳ Đang kiểm tra trạng thái thanh toán...
                            </div>
                        </div>
                    </div>

                    <div class="modal-footer d-flex justify-content-between">
                        <div class="small text-muted">Số tiền: <strong>{{ selectedCourse ?
                            formatPrice(selectedCourse.price, selectedCourse.currency) : '-' }}</strong></div>
                        <div>
                            <button class="btn btn-secondary me-2" data-bs-dismiss="modal"
                                @click="resetPayment">Đóng</button>
                            <button v-if="paymentStep === 'qr' && !isChecking" class="btn btn-success"
                                @click="simulatePaidManually">Đã thanh toán</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import axios from "axios";

export default {
    data() {
        return {
            courses: [],
            myCourses: [], // Danh sách khóa học đã đăng ký - CHỈ lấy từ API /my-courses
            studyPlans: [],
            selectedCourse: null,
            paymentStep: "info",
            isChecking: false,
            qrUrl: "",
            paymentInterval: null,
        };
    },

    computed: {
        // Lọc các khóa học chưa đăng ký để hiển thị ở danh sách bên trái
        // Sử dụng field isRegistered từ API để đảm bảo chính xác
        availableCourses() {
            // Chỉ hiển thị khóa học có isRegistered === false (chưa đăng ký)
            // Xử lý cả trường hợp isRegistered là undefined/null (coi như chưa đăng ký)
            return this.courses.filter(c => c.isRegistered !== true);
        },
        // Chỉ hiển thị các khóa học đã đăng ký từ API my-courses
        // Đảm bảo chỉ hiển thị khi thực sự có enrollment trong database
        registeredCourses() {
            // Đảm bảo chỉ trả về mảng, không bao giờ undefined
            // Chỉ hiển thị khóa học từ API /my-courses (đã có enrollment trong DB)
            if (!Array.isArray(this.myCourses)) {
                return [];
            }
            return this.myCourses;
        },
    },

    mounted() {
        this.loadData();
    },

    methods: {

        // Gộp toàn bộ gọi API vào 1 hàm loadData()
        loadData() {
            const studentId = 1; // Giả sử lấy từ auth hoặc context
            
            // Load tất cả khóa học (có field isRegistered từ backend)
            axios.get("http://localhost:5000/api/student/courses")
                .then(res => {
                    this.courses = Array.isArray(res.data.courses) ? res.data.courses : [];
                    console.log("✅ Đã tải courses:", this.courses.length, "khóa học");
                })
                .catch(err => {
                    console.error("❌ Lỗi tải courses:", err);
                    this.courses = [];
                });

            // Load khóa học đã đăng ký - CHỈ lấy từ API /my-courses
            // API này chỉ trả về khóa học có enrollment với status='active' trong database
            axios.get("http://localhost:5000/api/student/my-courses")
                .then(res => {
                    // Đảm bảo myCourses luôn là mảng rỗng nếu không có dữ liệu
                    const courses = res.data?.courses;
                    if (Array.isArray(courses)) {
                        this.myCourses = courses;
                        console.log("✅ Đã tải my-courses:", this.myCourses.length, "khóa học đã đăng ký");
                        
                        // Log để debug
                        if (this.myCourses.length > 0) {
                            console.log("Danh sách khóa học đã đăng ký:", this.myCourses.map(c => `${c.title} (ID: ${c.id})`));
                        } else {
                            console.log("✅ Chưa có khóa học nào được đăng ký - phần 'Khóa học của tôi' sẽ trống");
                        }
                    } else {
                        // Nếu không phải mảng, set thành mảng rỗng
                        console.warn("⚠️ API trả về dữ liệu không đúng format, set myCourses = []");
                        this.myCourses = [];
                    }
                })
                .catch(err => {
                    console.error("❌ Lỗi tải my-courses:", err);
                    // Đảm bảo luôn là mảng rỗng khi có lỗi
                    this.myCourses = [];
                    console.log("✅ Đã set myCourses = [] do lỗi");
                });

            // axios.get(`http://localhost:5000/api/student/study-plans/${studentId}`)
            //     .then(res => {
            //         this.studyPlans = res.data.plans || [];
            //     })
            //     .catch(err => console.error("Lỗi tải studyPlans:", err));
        },

        // ===== Các hàm tiện ích cơ bản =====
        formatPrice(value, currency = "VND") {
            if (value === 0) return "Miễn phí";
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
            // Gọi API đăng ký khóa học
            axios.post("http://localhost:5000/api/student/register", { courseId: course.id })
                .then((response) => {
                    // Kiểm tra response từ backend
                    if (response.data && response.data.success === true) {
                        console.log("✅ Backend xác nhận đăng ký thành công:", response.data);
                        
                        // CHỈ reload lại data từ backend sau khi backend đã xử lý thành công và commit vào database
                        // Không tự động thêm vào myCourses ở frontend - phải lấy từ API
                        Promise.all([
                            axios.get("http://localhost:5000/api/student/courses"),
                            axios.get("http://localhost:5000/api/student/my-courses")
                        ])
                            .then(([coursesRes, myCoursesRes]) => {
                                // Cập nhật từ response của backend - đảm bảo luôn là mảng
                                this.courses = Array.isArray(coursesRes.data.courses) ? coursesRes.data.courses : [];
                                this.myCourses = Array.isArray(myCoursesRes.data.courses) ? myCoursesRes.data.courses : [];
                                
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
                    console.error("❌ Lỗi khi đăng ký khóa học:", error);
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
            this.isChecking = true;
            if (this.paymentInterval) clearInterval(this.paymentInterval);

            this.paymentInterval = setInterval(() => {
                axios.post("/api/payment/status", { courseId: course.id })
                    .then(res => {
                        if (res.data.paid) {
                            clearInterval(this.paymentInterval);
                            this.isChecking = false;
                            
                            // Đăng ký khóa học sau khi thanh toán thành công
                            // CHỈ khi backend xử lý thành công thì mới reload data
                            axios.post("http://localhost:5000/api/student/register", { courseId: course.id })
                                .then((response) => {
                                    // Kiểm tra response từ backend
                                    if (response.data && response.data.success === true) {
                                        console.log("✅ Backend xác nhận đăng ký sau thanh toán tự động:", response.data);
                                        
                                        // CHỈ reload lại data từ backend sau khi backend đã xử lý thành công và commit vào database
                                        Promise.all([
                                            axios.get("http://localhost:5000/api/student/courses"),
                                            axios.get("http://localhost:5000/api/student/my-courses")
                                        ])
                                            .then(([coursesRes, myCoursesRes]) => {
                                                // Cập nhật từ response của backend - đảm bảo luôn là mảng
                                                this.courses = Array.isArray(coursesRes.data.courses) ? coursesRes.data.courses : [];
                                                this.myCourses = Array.isArray(myCoursesRes.data.courses) ? myCoursesRes.data.courses : [];
                                                
                                                console.log("✅ Đã reload sau thanh toán tự động - myCourses:", this.myCourses.length);
                                                
                                                const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal);
                                                if (modal) modal.hide();
                                                alert("✅ Thanh toán thành công! Khóa học đã được đăng ký.");
                                            })
                                            .catch(err => {
                                                console.error("❌ Lỗi reload sau thanh toán:", err);
                                                this.loadData();
                                                alert("✅ Thanh toán thành công!");
                                            });
                                    } else {
                                        console.warn("⚠️ Backend trả về nhưng success=False:", response.data);
                                        alert("✅ Thanh toán thành công! (Nhưng không thể đăng ký khóa học)");
                                    }
                                })
                                .catch((error) => {
                                    console.error("❌ Lỗi khi đăng ký khóa học sau thanh toán:", error);
                                    alert("✅ Thanh toán thành công! (Nhưng không thể đăng ký khóa học)");
                                });
                        }
                    })
                    .catch(() => console.warn("Lỗi khi kiểm tra thanh toán"));
            }, 3000);
        },

        simulatePaidManually() {
            if (!this.selectedCourse) return;
            
            // Gọi API đăng ký khóa học sau khi thanh toán
            // CHỈ khi backend xử lý thành công thì mới reload data
            axios.post("http://localhost:5000/api/student/register", { courseId: this.selectedCourse.id })
                .then((response) => {
                    // Kiểm tra response từ backend
                    if (response.data && response.data.success === true) {
                        console.log("✅ Backend xác nhận đăng ký sau thanh toán:", response.data);
                        
                        // CHỈ reload lại data từ backend sau khi backend đã xử lý thành công và commit vào database
                        Promise.all([
                            axios.get("http://localhost:5000/api/student/courses"),
                            axios.get("http://localhost:5000/api/student/my-courses")
                        ])
                            .then(([coursesRes, myCoursesRes]) => {
                                // Cập nhật từ response của backend - đảm bảo luôn là mảng
                                this.courses = Array.isArray(coursesRes.data.courses) ? coursesRes.data.courses : [];
                                this.myCourses = Array.isArray(myCoursesRes.data.courses) ? myCoursesRes.data.courses : [];
                                
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
.nav-tabs .nav-link {
    font-weight: 600;
    border-radius: 8px 8px 0 0;
    color: #555;
}

.hover-scale {
    transition: transform 0.25s ease;
}

.hover-scale:hover {
    transform: scale(1.02);
}

.object-fit-cover {
    object-fit: cover;
}

.card {
    transition: box-shadow 0.3s ease;
}

.card:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.btn {
    border-radius: 8px;
    font-weight: 500;
}

/* Styles bổ sung cho layout mới */
.list-group-item img {
    object-fit: cover;
}

.card-body.overflow-auto {
    max-height: 100%;
}

.col-md-6.d-flex.flex-column>.card.h-50 {
    min-height: 0;
    /* cho phép overflow-auto hoạt động trong flex column */
}
</style>