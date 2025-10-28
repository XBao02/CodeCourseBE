<template>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-7">
                <!-- Student Profile Card -->
                <div class="card shadow-lg border-0 rounded-3">
                    <div class="card-body text-center p-4">

                        <!-- Avatar (click để đổi ảnh) -->
                        <div class="profile-avatar mb-3 position-relative d-inline-block">
                            <img :src="student.photo" alt="Profile Picture"
                                class="rounded-circle border border-3 border-primary shadow" width="120" height="120"
                                style="cursor: pointer;" @click="triggerFileInput" />
                            <!-- hidden input -->
                            <input type="file" ref="fileInput" accept="image/*" class="d-none" @change="onFileChange" />
                            <small class="text-muted d-block mt-2">Click avatar to change photo</small>
                        </div>

                        <!-- Name -->
                        <h3 class="fw-bold mb-1">{{ student.name }}</h3>
                        <p class="text-muted mb-4">🎓 Student</p>

                        <hr />

                        <!-- Student Info -->
                        <div class="row text-start mb-4">
                            <div class="col-md-6 mb-3">
                                <strong>📛 Full Name:</strong><br />
                                {{ student.name }}
                            </div>
                            <div class="col-md-6 mb-3">
                                <strong>🎂 Date of Birth:</strong><br />
                                {{ student.dob }}
                            </div>
                            <div class="col-md-6 mb-3">
                                <strong>📞 Phone:</strong><br />
                                {{ student.phone }}
                            </div>
                            <div class="col-md-6 mb-3">
                                <strong>📧 Gmail:</strong><br />
                                {{ student.email }}
                            </div>
                            <div class="col-md-12 mb-3">
                                <strong>🏠 Address:</strong><br />
                                {{ student.address }}
                            </div>
                        </div>

                        <hr />

                        <!-- Courses -->
                        <h5 class="mb-3 fw-bold">📚 Enrolled Courses</h5>
                        <ul class="list-group mb-4">
                            <li class="list-group-item d-flex justify-content-between align-items-center"
                                v-for="course in student.courses" :key="course.id">
                                <span>{{ course.title }}</span>
                                <div class="progress w-50" style="height: 10px;">
                                    <div class="progress-bar bg-success" role="progressbar"
                                        :style="{ width: course.progress + '%' }" :aria-valuenow="course.progress"
                                        aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="badge bg-primary">{{ course.progress }}%</span>
                            </li>
                        </ul>

                        <!-- Actions -->
                        <div class="d-flex justify-content-center gap-3">
                            <button class="btn btn-outline-primary px-4" data-bs-toggle="modal"
                                data-bs-target="#editProfileModal">
                                Edit Profile
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Profile Modal -->
        <div class="modal fade" id="editProfileModal" tabindex="-1" aria-labelledby="editProfileLabel"
            aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content shadow-lg">
                    <div class="modal-header">
                        <h5 class="modal-title" id="editProfileLabel">Edit Profile</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="saveChanges">
                            <div class="mb-3">
                                <label class="form-label">Full Name</label>
                                <input v-model="editStudent.name" type="text" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Date of Birth</label>
                                <input v-model="editStudent.dob" type="date" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Phone</label>
                                <input v-model="editStudent.phone" type="text" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Gmail</label>
                                <input v-model="editStudent.email" type="email" class="form-control" required />
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Address</label>
                                <textarea v-model="editStudent.address" class="form-control" rows="2"></textarea>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Save Changes</button>
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
.profile-avatar img {
    object-fit: cover;
    transition: 0.3s;
}

.profile-avatar img:hover {
    opacity: 0.8;
    transform: scale(1.05);
}
</style>
