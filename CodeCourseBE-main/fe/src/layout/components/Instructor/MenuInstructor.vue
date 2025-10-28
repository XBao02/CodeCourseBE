<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-3">
        <div class="container-fluid">

            <!-- Logo -->
            <a class="navbar-brand d-flex align-items-center gap-2" href="#">
                <div class="d-flex align-items-center justify-content-center bg-success text-white fw-bold rounded"
                    style="width: 35px; height: 35px;">
                    CC
                </div>
                <div>
                    <div class="fw-bold">CodeClass</div>
                    <small class="text-muted">Manager</small>
                </div>
            </a>

            <!-- Menu items -->
            <ul class="navbar-nav mx-auto d-flex align-items-center gap-4">
                <li class="nav-item">
                    <router-link to="/instructor" class="nav-link d-flex align-items-center gap-2 fs-5">
                        🏠 Dashboard
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/courses" class="nav-link d-flex align-items-center gap-1 fs-5">
                        📚 Course Management
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/chat" class="nav-link d-flex align-items-center gap-1 fs-5">
                        💬 Student Chat
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/reports" class="nav-link d-flex align-items-center gap-1 fs-5">
                        📊 Reporting & Statistics
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/assistant" class="nav-link d-flex align-items-center gap-1 fs-5">
                        🤖 AI Assistant
                    </router-link>
                </li>
            </ul>

            <!-- Search and Right section -->
            <div class="d-flex align-items-center gap-3">
                <div class="search-container">
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="Search course or instruction,..." />
                        <span class="input-group-text">
                            <i class="fas fa-search"></i>
                        </span>
                    </div>
                </div>
                <button class="btn btn-light position-relative rounded-circle">
                    🔔
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                        3
                    </span>
                </button>

                <!-- User dropdown -->
                <div class="dropdown">
                    <button class="btn btn-light d-flex align-items-center gap-2" type="button"
                        data-bs-toggle="dropdown" aria-expanded="false">
                        <div class="rounded-circle bg-primary text-white fw-bold d-flex align-items-center justify-content-center"
                            style="width: 35px; height: 35px;">A</div>
                        <div class="text-start">
                            <div class="fw-bold">Demo User</div>
                            <small class="text-muted">Instructor</small>
                        </div>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow">
                        <li><a class="dropdown-item" href="#">Settings</a></li>
                        <li>
                            <hr class="dropdown-divider">
                        </li>
                        <li><a class="dropdown-item text-danger" href="#" @click="logout">Logout</a></li>
                    </ul>
                </div>
            </div>

        </div>
    </nav>
</template>

<script>
export default {
    data() {
        return {
            // Thêm dữ liệu nếu cần
        }
    },
    methods: {
        logout() {
            // localStorage.removeItem('token'); -> cái này khi làm bé hay mở ra
            this.$router.push('/');
        }
    },
};
</script>

<style scoped>
.nav-link {
    font-weight: 500;
    color: #444 !important;
}

.nav-link:hover {
    color: #0d6efd !important;
}

.search-container {
    margin-left: 10px;
}

.input-group {
    width: 400px;
    /* Tăng chiều rộng để to hơn */
    height: 50px;
    /* Tăng chiều cao để hình vuông */
}

.input-group .form-control {
    border-radius: 0;
    /* Loại bỏ bo góc để thành hình vuông */
    border-right: none;
    padding: 12px 16px;
    /* Tăng padding cho to hơn */
    height: 100%;
    /* Đảm bảo chiều cao khớp với input-group */
    font-size: 16px;
    /* Tăng kích thước chữ */
    border: 3px solid #ddd;
    /* Viền đậm hơn */
}

.input-group-text {
    background-color: #fff;
    border: 3px solid #ddd;
    /* Viền đậm hơn */
    border-left: none;
    border-radius: 0;
    /* Loại bỏ bo góc để thành hình vuông */
    padding: 12px 16px;
    /* Tăng padding cho to hơn */
    height: 100%;
    /* Đảm bảo chiều cao khớp với input-group */
    cursor: pointer;
}

.input-group-text .fas {
    color: #666;
    font-size: 18px;
    /* Tăng kích thước icon */
}
</style>