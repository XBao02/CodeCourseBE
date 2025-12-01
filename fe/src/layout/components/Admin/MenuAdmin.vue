<template>
    <nav class="admin-navbar">
        <div class="navbar-container">
            <!-- Logo -->
            <router-link to="/admin" class="navbar-logo">
                <div class="logo-icon">CC</div>
                <div class="logo-text">
                    <div class="logo-title">CodeClass</div>
                    <div class="logo-subtitle">Admin</div>
                </div>
            </router-link>
            
            <!-- Menu items -->
            <ul class="navbar-menu">
                <li class="nav-item">
                    <router-link to="/admin" exact class="nav-link">
                        Dashboard
                    </router-link>
                </li>

                <!-- Dropdown for Account Manager -->
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#"
                        :class="{ 'active': isAccountsActive }"
                        id="accountDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        Accounts
                    </a>
                    <ul class="dropdown-menu" aria-labelledby="accountDropdown">
                        <li>
                            <router-link to="/admin/students_manager" class="dropdown-item">
                                Students
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/admin/instructors_manager" class="dropdown-item">
                                Instructors
                            </router-link>
                        </li>
                    </ul>
                </li>

                <li class="nav-item">
                    <router-link to="/admin/courses" class="nav-link">
                        Courses
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/admin/reports" class="nav-link">
                        Reports
                    </router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/admin/decentralization" class="nav-link">
                        Permissions
                    </router-link>
                </li>
            </ul>

            <!-- User dropdown -->
            <div class="navbar-user">
                <div class="user-avatar-wrapper dropdown">
                    <div class="user-avatar" data-bs-toggle="dropdown" aria-expanded="false">A</div>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#">Settings</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" @click="logout">Logout</a></li>
                    </ul>
                </div>
            </div>

        </div>
    </nav>
</template>

<script>
export default {
    name: "MenuAdmin",
    data() {
        return {
            // Thêm dữ liệu nếu cần
        }
    },
    computed: {
        isAccountsActive() {
            const path = this.$route.path;
            return path.includes('/admin/students_manager') || path.includes('/admin/instructors_manager');
        }
    },
    methods: {
        logout() {
            // localStorage.removeItem('token'); -> cái này khi làm bé hay mở ra
            this.$router.push('/');
        }
    }
};
</script>

<style scoped>
.admin-navbar {
    position: sticky;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 40px;
}

.navbar-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 70px;
}

.navbar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    transition: all 0.3s ease;
}

.navbar-logo:hover {
    opacity: 0.8;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 700;
    font-size: 16px;
}

.logo-text {
    display: flex;
    flex-direction: column;
}

.logo-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.2;
}

.logo-subtitle {
    font-size: 12px;
    color: #666;
}

.navbar-menu {
    display: flex;
    align-items: center;
    gap: 32px;
    list-style: none;
    margin: 0;
    padding: 0;
    flex: 1;
    justify-content: center;
}

.nav-item {
    position: relative;
}

.nav-link {
    color: #666;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    padding: 8px 0;
    display: block;
    transition: all 0.3s ease;
    position: relative;
}

.nav-link::after {
    content: '';
    position: absolute;
    bottom: -23px;
    left: 0;
    width: 0;
    height: 3px;
    background: linear-gradient(90deg, #1f2937, #374151);
    transition: width 0.3s ease;
}

.nav-link:hover {
    color: #1a1a1a;
}

.nav-link.router-link-active,
.nav-link.active {
    color: #1a1a1a;
}

.nav-link.router-link-active::after,
.nav-link.active::after {
    width: 100%;
}

.dropdown-toggle {
    cursor: pointer;
}

.dropdown-menu {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 8px;
    margin-top: 8px;
}

.dropdown-item {
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 14px;
    color: #666;
    transition: all 0.2s ease;
}

.dropdown-item:hover {
    background: #f8f9fa;
    color: #1a1a1a;
}

.dropdown-item.router-link-active {
    background: #f8f9fa;
    color: #1a1a1a;
    font-weight: 500;
}

.navbar-user {
    display: flex;
    align-items: center;
}

.user-avatar-wrapper {
    position: relative;
}

.user-avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #1f2937, #374151);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-weight: 700;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.user-avatar:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
    .admin-navbar {
        padding: 0 20px;
    }

    .navbar-menu {
        display: none;
    }
}
</style>
