<template>
    <div class="profile-wrapper">
        <!-- Header -->
        <div class="profile-header">
            <h1>My Profile</h1>
            <p>Manage your personal information and settings</p>
        </div>

        <div class="profile-content">
            <!-- Profile Card -->
            <div class="profile-card">
                <!-- Avatar -->
                <div class="avatar-section">
                    <img :src="student.photo" alt="Profile Picture" class="profile-avatar" @click="triggerFileInput" />
                    <input type="file" ref="fileInput" accept="image/*" class="d-none" @change="onFileChange" />
                    <small class="avatar-hint">Click avatar to change photo</small>
                </div>

                <!-- Name -->
                <h2>{{ student.name }}</h2>
                <p class="role-badge">Student</p>

                <!-- Student Info -->
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Full Name</span>
                        <span class="info-value">{{ student.name }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Date of Birth</span>
                        <span class="info-value">{{ student.dob }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone</span>
                        <span class="info-value">{{ student.phone }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email</span>
                        <span class="info-value">{{ student.email }}</span>
                    </div>
                    <div class="info-item full-width">
                        <span class="info-label">Address</span>
                        <span class="info-value">{{ student.address }}</span>
                    </div>
                </div>

                <!-- Courses -->
                <div class="courses-section">
                    <h5>Enrolled Courses</h5>
                    <div class="courses-list">
                        <div class="course-progress-item" v-for="course in student.courses" :key="course.id">
                            <div class="course-info">
                                <span class="course-title">{{ course.title }}</span>
                                <span class="course-percent">{{ course.progress }}%</span>
                            </div>
                            <div class="progress-bar-wrapper">
                                <div class="progress-bar-fill" :style="{ width: course.progress + '%' }"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="profile-actions">
                    <button class="action-button" data-bs-toggle="modal" data-bs-target="#editProfileModal">
                        Edit Profile
                    </button>
                </div>
            </div>
        </div>

        <!-- Edit Profile Modal -->
        <div class="modal fade" id="editProfileModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Profile</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="saveChanges">
                            <div class="form-group">
                                <label>Full Name</label>
                                <input v-model="editStudent.name" type="text" class="form-input" required />
                            </div>
                            <div class="form-group">
                                <label>Date of Birth</label>
                                <input v-model="editStudent.dob" type="date" class="form-input" required />
                            </div>
                            <div class="form-group">
                                <label>Phone</label>
                                <input v-model="editStudent.phone" type="text" class="form-input" required />
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input v-model="editStudent.email" type="email" class="form-input" required />
                            </div>
                            <div class="form-group">
                                <label>Address</label>
                                <textarea v-model="editStudent.address" class="form-input" rows="2"></textarea>
                            </div>
                            <button type="submit" class="action-button full-width">Save Changes</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
export default {
    name: "StudentProfile",
    data() {
        return {
            student: {
                name: "Nguyen Van A",
                dob: "2002-05-15",
                phone: "+84 987 654 321",
                email: "nguyenvana@student.edu.vn",
                address: "45 Tran Hung Dao, Da Nang, Vietnam",
                photo: "https://img.lovepik.com/free-png/20211204/lovepik-cartoon-avatar-png-image_401302777_wh1200.png",
                courses: [
                    { id: 1, title: "Frontend Development", progress: 75 },
                    { id: 2, title: "Database Management", progress: 50 },
                    { id: 3, title: "Backend Development", progress: 20 },
                ],
            },
            editStudent: {}
        };
    },
    methods: {
        triggerFileInput() {
            this.$refs.fileInput.click();
        },
        onFileChange(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    this.student.photo = e.target.result; // hiển thị ảnh mới
                };
                reader.readAsDataURL(file);
            }
        },
        saveChanges() {
            this.student = { ...this.editStudent, photo: this.student.photo };
            const modalEl = document.getElementById("editProfileModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
        }
    },
    mounted() {
        this.editStudent = { ...this.student };
    }
};
</script>

<style scoped>
.profile-wrapper {
    background: #f8f9fa;
    min-height: 100vh;
    padding: 40px;
}

.profile-header {
    margin-bottom: 40px;
}

.profile-header h1 {
    font-size: 32px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.profile-header p {
    color: #666;
    font-size: 15px;
    margin: 0;
}

.profile-content {
    max-width: 800px;
    margin: 0 auto;
}

.profile-card {
    background: white;
    padding: 40px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    text-align: center;
}

.avatar-section {
    margin-bottom: 24px;
}

.profile-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #e5e7eb;
    cursor: pointer;
    transition: all 0.3s ease;
}

.profile-avatar:hover {
    opacity: 0.8;
    transform: scale(1.05);
}

.avatar-hint {
    display: block;
    margin-top: 8px;
    color: #999;
    font-size: 13px;
}

.profile-card h2 {
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px 0;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #dbeafe;
  color: #2563eb;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 32px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 32px;
    text-align: left;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.info-item.full-width {
    grid-column: 1 / -1;
}

.info-label {
    font-size: 13px;
    color: #666;
    font-weight: 500;
}

.info-value {
    font-size: 15px;
    color: #1a1a1a;
}

.courses-section {
    margin-bottom: 32px;
    text-align: left;
}

.courses-section h5 {
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 16px 0;
}

.courses-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.course-progress-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.course-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.course-title {
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
}

.course-percent {
    font-size: 14px;
    font-weight: 600;
    color: #666;
}

.progress-bar-wrapper {
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    transition: width 0.3s ease;
}

.profile-actions {
    text-align: center;
}

.action-button {
  padding: 12px 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.action-button.full-width {
    width: 100%;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
    margin-bottom: 6px;
}

.form-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.2s ease;
}

.form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

@media (max-width: 768px) {
    .profile-wrapper {
        padding: 20px;
    }

    .profile-card {
        padding: 24px;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }
}
</style>
