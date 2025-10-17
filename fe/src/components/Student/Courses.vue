<template>
    <div class="container py-5">
        <!-- Tabs chuyển qua lại -->
        <ul class="nav nav-tabs justify-content-start mb-4">
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'available' }" href="#"
                    @click.prevent="activeTab = 'available'">
                    📘 Khóa học chưa đăng ký
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'registered' }" href="#"
                    @click.prevent="activeTab = 'registered'">
                    ✅ Khóa học của tôi
                </a>
            </li>
        </ul>

        <!-- Nội dung tab: khóa học chưa đăng ký -->
        <div v-if="activeTab === 'available'">
            <div class="row g-4">
                <div v-for="(course, index) in availableCourses" :key="index" class="col-md-6 col-lg-3">
                    <div class="card border-0 shadow-sm rounded-4 h-100 hover-scale overflow-hidden">
                        <img :src="course.image" class="card-img-top object-fit-cover" height="160" />
                        <div class="card-body d-flex flex-column justify-content-between">
                            <div>
                                <h6 class="fw-bold mb-1 text-dark">{{ course.name }}</h6>
                                <p class="text-muted small mb-1">{{ course.instructor }}</p>
                                <span class="badge bg-info text-dark me-1">{{ course.level }}</span>
                                <span class="text-muted small"><i class="fas fa-user-graduate me-1"></i>{{
                                    course.students }}</span>
                            </div>
                            <div class="mt-3">
                                <p class="fw-semibold mb-2">
                                    <span v-if="course.price === 0" class="text-success">Miễn phí</span>
                                    <span v-else class="text-primary">{{ formatPrice(course.price) }}</span>
                                </p>

                                <button v-if="course.price === 0" class="btn btn-success w-100 btn-sm"
                                    @click="registerCourse(course)">
                                    <i class="fas fa-check-circle me-2"></i>Đăng ký miễn phí
                                </button>

                                <button v-else class="btn btn-outline-primary w-100 btn-sm"
                                    @click="openPayment(course)">
                                    <i class="fas fa-credit-card me-2"></i>Thanh toán
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Nội dung tab: khóa học của tôi -->
        <div v-else>
            <div v-if="registeredCourses.length" class="row g-4">
                <div v-for="(course, index) in registeredCourses" :key="'reg-' + index" class="col-md-6 col-lg-3">
                    <div class="card border-0 shadow rounded-4 h-100 hover-scale overflow-hidden">
                        <img :src="course.image" class="card-img-top object-fit-cover" height="160" />
                        <div class="card-body d-flex flex-column justify-content-between">
                            <div>
                                <h6 class="fw-bold mb-1">{{ course.name }}</h6>
                                <p class="text-muted small mb-1">{{ course.instructor }}</p>
                            </div>
                            <button class="btn btn-primary w-100 btn-sm" @click="goToCourse(course)">
                                <i class="fas fa-play me-1"></i>Vào học ngay
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-else class="text-center text-muted py-5">
                <i class="fas fa-info-circle me-2"></i>Bạn chưa đăng ký khóa học nào.
            </div>
        </div>

        <!-- Modal thanh toán -->
        <div class="modal fade" id="paymentModal" tabindex="-1" ref="paymentModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content rounded-4 shadow">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title fw-semibold">💳 Thanh toán khóa học</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div v-if="selectedCourse">
                            <h6 class="fw-bold">{{ selectedCourse.name }}</h6>
                            <p class="text-muted small">Giảng viên: {{ selectedCourse.instructor }}</p>
                            <p><strong>Phí khóa học:</strong>
                                <span class="text-primary">{{ formatPrice(selectedCourse.price) }}</span>
                            </p>
                            <hr />
                            <h6 class="fw-semibold mb-2">Mã QR thanh toán:</h6>
                            <div class="text-center">
                                <img src="https://img.vietqr.io/image/970422-123456789-BR4iNHoJ.jpg" alt="QR Code"
                                    class="rounded shadow-sm border p-2" width="200" />
                                <p class="small text-secondary mt-2">Quét mã để thanh toán bằng ngân hàng nội địa.</p>
                                <div v-if="isChecking" class="text-info small mt-2">
                                    ⏳ Đang kiểm tra trạng thái thanh toán...
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer d-flex justify-content-end">
                        <button class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            activeTab: "available",
            courses: [
                {
                    name: "Basic Java Programming",
                    instructor: "Dr. Davis Marcos",
                    level: "Beginner",
                    price: 500000,
                    students: 1200,
                    image: "https://cdn.elearningindustry.com/wp-content/uploads/2020/02/learn-java-programming.jpg",
                    isRegistered: false,
                },
                {
                    name: "Python for Beginners",
                    instructor: "Dr. Sophie Alden",
                    level: "Beginner",
                    price: 0,
                    students: 2200,
                    image: "https://i0.wp.com/data-flair.training/blogs/wp-content/uploads/sites/2/2018/02/Python-Tutorial-Feature-Image.jpg",
                    isRegistered: false,
                },
                {
                    name: "Web Development Bootcamp",
                    instructor: "Mr. John Walker",
                    level: "Intermediate",
                    price: 750000,
                    students: 1800,
                    image: "https://miro.medium.com/v2/resize:fit:1400/1*kj1SxYwNqZpk2JxwRkIobg.jpeg",
                    isRegistered: false,
                },
                {
                    name: "UI/UX Design Masterclass",
                    instructor: "Ms. Emily Carter",
                    level: "Intermediate",
                    price: 650000,
                    students: 900,
                    image: "https://cdn.dribbble.com/users/1787323/screenshots/14707522/media/7b3a1d3e063abda39a6b32a90e3e68b3.png",
                    isRegistered: false,
                },
                {
                    name: "Machine Learning A-Z",
                    instructor: "Dr. Alan Turing",
                    level: "Advanced",
                    price: 1200000,
                    students: 1500,
                    image: "https://miro.medium.com/v2/resize:fit:1400/1*X3UwYHw2rWT1nDuwtSf6xw.jpeg",
                    isRegistered: false,
                },
            ],
            selectedCourse: null,
            isChecking: false,
        };
    },
    computed: {
        availableCourses() {
            return this.courses.filter((c) => !c.isRegistered);
        },
        registeredCourses() {
            return this.courses.filter((c) => c.isRegistered);
        },
    },
    methods: {
        formatPrice(value) {
            if (value === 0) return "Miễn phí";
            return value.toLocaleString("vi-VN") + "₫";
        },
        registerCourse(course) {
            course.isRegistered = true;
        },
        openPayment(course) {
            this.selectedCourse = course;
            const modal = new bootstrap.Modal(this.$refs.paymentModal);
            modal.show();
            this.startPaymentCheck(course);
        },
        async startPaymentCheck(course) {
            this.isChecking = true;

            // Giả lập gọi API ngân hàng để kiểm tra trạng thái thanh toán
            const interval = setInterval(async () => {
                const res = await this.mockBankAPI(course);

                if (res.paid) {
                    clearInterval(interval);
                    this.isChecking = false;
                    course.isRegistered = true;
                    const modal = bootstrap.Modal.getInstance(this.$refs.paymentModal);
                    modal.hide();
                    this.selectedCourse = null;
                    this.activeTab = "registered";
                    alert("✅ Thanh toán thành công! Khóa học đã được thêm vào danh sách của bạn.");
                }
            }, 3000);
        },
        async mockBankAPI(course) {
            // 🔹 Giả lập phản hồi API (có thể thay bằng gọi fetch API thật)
            await new Promise((r) => setTimeout(r, 1000));
            const paid = Math.random() > 0.7; // 30% cơ hội trả về "đã thanh toán"
            return { paid };
        },
        goToCourse(course) {
            this.$router.push(`/course/${course.name.replace(/\s+/g, "-")}`);
        },
    },
};
</script>

<style scoped>
.nav-tabs .nav-link {
    font-weight: 600;
    border-radius: 8px 8px 0 0;
    color: #555;
}

.nav-tabs .nav-link.active {
    background-color: #0d6efd;
    color: white !important;
}

.hover-scale {
    transition: transform 0.25s ease;
}

.hover-scale:hover {
    transform: scale(1.03);
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
</style>
