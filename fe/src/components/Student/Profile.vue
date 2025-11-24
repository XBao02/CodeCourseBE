<template>
    <div class="min-vh-100 bg-gradient py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    
                    <div class="profile-header">
                        <div class="decorative-circle circle-1"></div>
                        <div class="decorative-circle circle-2"></div>
                        
                        <div class="row align-items-center position-relative">
                            <div class="col-md-3 text-center">
                                <div class="avatar-wrapper position-relative d-inline-block">
                                    <img :src="student.photo" alt="Profile" 
                                            class="profile-avatar" 
                                            @click="triggerFileInput" />
                                    <div class="avatar-overlay" @click="triggerFileInput">
                                        <font-awesome-icon :icon="['fas', 'camera-alt']" />
                                    </div>
                                    <input type="file" ref="fileInput" accept="image/*" 
                                            class="d-none" @change="onFileChange" />
                                </div>
                            </div>

                            <div class="col-md-6 text-center text-md-start mt-3 mt-md-0">
                                <input v-if="isEditing" 
                                        v-model="editStudent.fullName" 
                                        type="text" 
                                        class="form-control form-control-lg fw-bold text-center text-md-start mb-2 name-input" 
                                        placeholder="Enter your name" />
                                <h1 v-else class="display-5 fw-bold text-white mb-2">{{ student.fullName }}</h1>
                                <p class="text-white-50 fs-5 mb-0"><font-awesome-icon :icon="['fas', 'user']" /> Student Profile</p>
                            </div>

                            <div class="col-md-3 text-center text-md-end mt-3 mt-md-0">
                                <button v-if="!isEditing" 
                                         class="btn btn-light btn-lg px-4 rounded-pill shadow"
                                         @click="startEdit">
                                    <i class="bi bi-pencil-square me-2"></i>Edit Profile
                                </button>
                                <div v-else class="d-flex gap-2 justify-content-center justify-content-md-end">
                                    <button class="btn btn-success rounded-pill px-4" @click="saveChanges">
                                        <i class="bi bi-check-lg me-2"></i>Save
                                    </button>
                                    <button class="btn btn-danger rounded-pill px-4" @click="cancelEdit">
                                        <i class="bi bi-x-lg me-2"></i>Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="content-card">
                        
                        <div class="row g-4 mb-5">
                            
                            <div class="col-md-6">
                                <div class="info-card info-card-blue">
                                    <div class="info-icon bg-primary">
                                        <font-awesome-icon :icon="['fas', 'calendar-alt']" />
                                    </div>
                                    <div class="info-content">
                                        <label class="info-label">Date of Birth</label>
                                        <input v-if="isEditing" 
                                                v-model="editStudent.dob" 
                                                type="date" 
                                                class="form-control form-control-sm" />
                                        <p v-else class="info-value">{{ student.dob }}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="info-card info-card-green">
                                    <div class="info-icon bg-success">
                                        <font-awesome-icon :icon="['fas', 'phone-alt']" />
                                    </div>
                                    <div class="info-content">
                                        <label class="info-label">Phone Number</label>
                                        <input v-if="isEditing" 
                                                v-model="editStudent.phone" 
                                                type="text" 
                                                class="form-control form-control-sm" />
                                        <p v-else class="info-value">{{ student.phone }}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="info-card info-card-purple">
                                    <div class="info-icon bg-purple">
                                        <font-awesome-icon :icon="['fas', 'envelope']" />
                                    </div>
                                    <div class="info-content">
                                        <label class="info-label">Email Address</label>
                                        <input v-if="isEditing" 
                                                v-model="editStudent.email" 
                                                type="email" 
                                                class="form-control form-control-sm" />
                                        <p v-else class="info-value">{{ student.email }}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="info-card info-card-orange">
                                    <div class="info-icon bg-warning">
                                        <font-awesome-icon :icon="['fas', 'map-marker-alt']" />
                                    </div>
                                    <div class="info-content">
                                        <label class="info-label">Address</label>
                                        <textarea v-if="isEditing" 
                                                 v-model="editStudent.address" 
                                                 class="form-control form-control-sm" 
                                                 rows="2"></textarea>
                                        <p v-else class="info-value">{{ student.address }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="courses-section">
                            <div class="section-header mb-4">
                                <div class="section-icon">
                                    <font-awesome-icon :icon="['fas', 'book']" />
                                </div>
                                <h2 class="section-title">Enrolled Courses</h2>
                            </div>

                            <div class="row g-4">
                                <div v-for="course in student.courses" 
                                            :key="course.id" 
                                            class="col-12">
                                    <div class="course-card">
                                        <div class="d-flex justify-content-between align-items-center mb-3">
                                            <h5 class="course-title mb-0">{{ course.title }}</h5>
                                            <span class="progress-badge">{{ course.progress }}%</span>
                                        </div>
                                        <div class="progress-wrapper">
                                            <div class="progress">
                                                <div class="progress-bar progress-bar-animated" 
                                                        :class="'bg-' + course.color"
                                                        :style="{ width: course.progress + '%' }">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'; 

// Khai báo Base URL
const API_BASE_URL = 'http://localhost:5000/api/students';

export default {
    name: "ModernStudentProfile",
    data() {
        return {
            // ⚠️ CẦN THAY ĐỔI: Đây là ID sinh viên bạn muốn lấy dữ liệu.
            studentId: 1, 
            
            // Dữ liệu ban đầu (Đã loại bỏ dữ liệu cố định, chỉ giữ cấu trúc)
            student: {
                fullName: "",
                dob: "",
                phone: "",
                email: "",
                address: "",
                photo: "https://img.lovepik.com/free-png/20211204/lovepik-cartoon-avatar-png-image_401302777_wh1200.png",
                // Khóa học vẫn là dữ liệu mẫu vì chưa có API cho phần này
                courses: [
                    { id: 1, title: "Frontend Development", progress: 75, color: "primary" },
                    { id: 2, title: "Database Management", progress: 50, color: "info" },
                    { id: 3, title: "Backend Development", progress: 20, color: "success" },
                ],
            },
            editStudent: {},
            isEditing: false
        };
    },
    // Gọi hàm fetchStudentData() khi component được tạo
    created() {
        this.fetchStudentData(); 
    },
    methods: {
        // ===============================================
        // HÀM FETCH DATA: Lấy dữ liệu từ Database
        // ===============================================
        async fetchStudentData() {
            const url = `${API_BASE_URL}/${this.studentId}`;
            try {
                const response = await axios.get(url);
                
                if (response.data.status === 'success' && response.data.data) {
                    const fetchedData = response.data.data;
                    
                    // Ghi đè dữ liệu mẫu bằng dữ liệu từ API
                    this.student.fullName = fetchedData.name || fetchedData.fullName || 'N/A';
                    this.student.dob = fetchedData.dob || 'N/A';
                    this.student.phone = fetchedData.phone || 'N/A';
                    this.student.email = fetchedData.email || 'N/A';
                    this.student.address = fetchedData.address || 'N/A';
                    this.student.major = fetchedData.major || 'N/A';
                    
                    // Lưu ý: Trường 'name' trong DB được ánh xạ thành 'fullName' trong Vue state
                } else {
                    console.warn(`Không tìm thấy dữ liệu sinh viên ID ${this.studentId} từ API.`);
                    alert(`Lỗi: Không tìm thấy sinh viên ID ${this.studentId}.`);
                }
            } catch (error) {
                console.error("Lỗi khi tải dữ liệu sinh viên:", error);
                alert(`Lỗi kết nối API: ${error.message}. Vui lòng kiểm tra Backend.`);
            }
        },

        triggerFileInput() {
            this.$refs.fileInput.click();
        },
        onFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    this.student.photo = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        },
        startEdit() {
            // Sao chép toàn bộ dữ liệu hiện tại để chỉnh sửa
            this.editStudent = { ...this.student };
            this.isEditing = true;
        },

        // ===============================================
        // HÀM SAVE CHANGES: Gửi yêu cầu PATCH và Refresh
        // ===============================================
        async saveChanges() {
            const url = `${API_BASE_URL}/${this.studentId}`;
            
            // Dữ liệu gửi đi (Ánh xạ fullName thành 'name' để khớp với tham số trong API Python)
            const payload = {
                name: this.editStudent.fullName, 
                dob: this.editStudent.dob,
                phone: this.editStudent.phone,
                email: this.editStudent.email,
                address: this.editStudent.address,
                major: this.editStudent.major, 
            };
            
            try {
                const response = await axios.patch(url, payload);

                if (response.data.status === 'success') {
                    
                    // Tải lại dữ liệu chính thức từ server sau khi cập nhật thành công
                    await this.fetchStudentData(); 
                    
                    this.isEditing = false;
                    alert('Cập nhật thông tin sinh viên thành công!');
                } else {
                    alert(`Lỗi cập nhật: ${response.data.message}`);
                }

            } catch (error) {
                const errorMessage = error.response?.data?.message || 'Lỗi kết nối hoặc lỗi server. Vui lòng kiểm tra console.';
                console.error("Lỗi khi gửi yêu cầu PATCH:", error);
                alert(`Cập nhật thất bại: ${errorMessage}`);
            }
        },

        cancelEdit() {
            this.editStudent = {};
            this.isEditing = false;
        }
    }
};
</script>

<style scoped>
/* Background Gradient */
.bg-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Profile Header */
.profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px 20px 0 0;
    padding: 3rem 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.decorative-circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
}

.circle-1 {
    width: 300px;
    height: 300px;
    top: -150px;
    right: -100px;
}

.circle-2 {
    width: 200px;
    height: 200px;
    bottom: -100px;
    left: -50px;
}

/* Avatar */
.avatar-wrapper {
    cursor: pointer;
}

.profile-avatar {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    object-fit: cover;
    border: 5px solid white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    transition: transform 0.3s ease;
}

.profile-avatar:hover {
    transform: scale(1.05);
}

.avatar-overlay {
    position: absolute;
    bottom: 5px;
    right: 5px;
    background: white;
    color: #667eea;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

.avatar-overlay:hover {
    background: #667eea;
    color: white;
    transform: scale(1.1);
}

/* Content Card */
.content-card {
    background: white;
    border-radius: 0 0 20px 20px;
    padding: 3rem 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* Info Cards */
.info-card {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    border-radius: 15px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.info-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.info-card-blue {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-color: #2196f3;
}

.info-card-green {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border-color: #4caf50;
}

.info-card-purple {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border-color: #9c27b0;
}

.info-card-orange {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border-color: #ff9800;
}

.info-icon {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.bg-purple {
    background: #9c27b0;
}

.info-content {
    flex: 1;
}

.info-label {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.25rem;
    display: block;
    font-weight: 500;
}

.info-value {
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 0;
}

/* Courses Section */
.courses-section {
    border-top: 2px solid #f0f0f0;
    padding-top: 2rem;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.section-icon {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
}

.section-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #333;
    margin: 0;
}

/* Course Card */
.course-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid #dee2e6;
    transition: all 0.3s ease;
}

.course-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.course-title {
    font-weight: 600;
    color: #333;
}

.progress-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.progress-wrapper {
    margin-top: 0.5rem;
}

.progress {
    height: 12px;
    border-radius: 10px;
    background-color: #e9ecef;
    overflow: hidden;
}

.progress-bar {
    border-radius: 10px;
    transition: width 0.6s ease;
}

/* Form Controls */
.form-control-sm {
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    padding: 0.5rem;
    font-weight: 600;
}

.form-control-sm:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.name-input {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid white;
    color: #333;
    font-size: 2rem;
}

.name-input:focus {
    border-color: white;
    box-shadow: 0 0 0 0.3rem rgba(255, 255, 255, 0.5);
    background: white;
}

/* Responsive */
@media (max-width: 768px) {
    .profile-header {
        padding: 2rem 1rem;
    }
    
    .content-card {
        padding: 2rem 1rem;
    }
}
</style>
