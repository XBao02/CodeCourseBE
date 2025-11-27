<template>
    <nav class="navbar">
        <div class="navbar-container">

            <!-- Logo -->
            <a class="navbar-logo" href="/">
                <div class="logo-box">CC</div>
                <div class="logo-text">
                    <div class="logo-title">CodeClass</div>
                    <small class="logo-subtitle">Manager</small>
                </div>
            </a>

            <!-- Menu items -->
            <ul class="navbar-menu">
                <li class="nav-item">
                    <router-link to="/instructor" exact class="nav-link">Dashboard</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/courses" class="nav-link">Course Management</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/chat" class="nav-link">Student Chat</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/reports" class="nav-link">Reporting & Statistics</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/instructor/assistant" class="nav-link">AI Assistant</router-link>
                </li>
            </ul>

            <!-- Search and Right section -->
            <div class="navbar-right">
                <div class="search-container">
                    <input type="text" class="search-input" placeholder="Search course or instruction...">
                </div>
                <button class="notification-btn">
                    Notifications
                    <span class="notification-badge">3</span>
                </button>

                <!-- User dropdown -->
                <div class="dropdown">
                    <button class="user-btn" @click="toggleDropdown">
                        <div class="user-avatar">A</div>
                        <div class="user-info">
                            <div class="user-name">Demo User</div>
                            <small class="user-role">Instructor</small>
                        </div>
                    </button>
                    <ul v-if="showDropdown" class="dropdown-menu">
                        <li><a href="#" @click.prevent="goToSettings">Settings</a></li>
                        <li class="divider"></li>
                        <li><a href="#" @click.prevent="logout" class="logout">Logout</a></li>
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
            showDropdown: false
        }
    },
    methods: {
        toggleDropdown() {
            this.showDropdown = !this.showDropdown;
        },
        goToSettings() {
            this.showDropdown = false;
            this.$router.push('/instructor/settings');
        },
        logout() {
            this.showDropdown = false;
            localStorage.removeItem('token');
            localStorage.removeItem('userInfo');
            this.$router.push('/');
        }
    },
    mounted() {
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                this.showDropdown = false;
            }
        });
    }
};
</script>

<style scoped>
.navbar {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.navbar-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 70px;
    gap: 24px;
}

.navbar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 600;
    flex-shrink: 0;
}

.logo-box {
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1f2937;
    color: white;
    font-weight: 700;
    font-size: 14px;
    width: 36px;
    height: 36px;
    border-radius: 6px;
}

.logo-text {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.logo-title {
    font-size: 14px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.logo-subtitle {
    font-size: 12px;
    color: #999;
    margin: 0;
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
    margin: 0;
}

.nav-link {
    font-size: 14px;
    font-weight: 500;
    color: #666;
    text-decoration: none;
    transition: color 0.2s ease;
    position: relative;
    padding-bottom: 4px;
}

.nav-link:hover {
    color: #1a1a1a;
}

.nav-link.router-link-exact-active {
    color: #1a1a1a;
}

.nav-link.router-link-exact-active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: #1f2937;
}

.navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
}

.search-container {
    position: relative;
}

.search-input {
    width: 300px;
    padding: 10px 14px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    background: #f9fafb;
    transition: all 0.2s ease;
}

.search-input::placeholder {
    color: #9ca3af;
}

.search-input:focus {
    outline: none;
    border-color: #3b82f6;
    background: white;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.notification-btn {
    background: none;
    border: 1px solid #d1d5db;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 18px;
    position: relative;
    transition: all 0.2s ease;
}

.notification-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.notification-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    background: #ef4444;
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 50%;
    min-width: 20px;
    text-align: center;
}

.dropdown {
    position: relative;
}

.user-btn {
    background: none;
    border: 1px solid #d1d5db;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s ease;
}

.user-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.user-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: #3b82f6;
    color: white;
    font-weight: 600;
    font-size: 14px;
    border-radius: 6px;
}

.user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.user-name {
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
}

.user-role {
    font-size: 12px;
    color: #999;
    margin: 0;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    margin-top: 8px;
    padding: 6px 0;
    list-style: none;
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    min-width: 160px;
}

.dropdown-menu li a {
    display: block;
    padding: 10px 16px;
    color: #374151;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.2s ease;
}

.dropdown-menu li a:hover {
    background: #f9fafb;
    color: #1a1a1a;
}

.dropdown-menu li a.logout {
    color: #ef4444;
}

.dropdown-menu li a.logout:hover {
    background: #fef2f2;
}

.dropdown-menu .divider {
    height: 1px;
    background: #e5e7eb;
    margin: 6px 0;
}

@media (max-width: 1024px) {
    .navbar-menu {
        gap: 20px;
    }

    .search-input {
        width: 200px;
    }
}

@media (max-width: 768px) {
    .navbar-container {
        padding: 0 16px;
        height: 60px;
        gap: 12px;
    }

    .navbar-menu {
        display: none;
    }

    .search-input {
        width: 150px;
        font-size: 13px;
    }

    .logo-title {
        font-size: 13px;
    }

    .logo-subtitle {
        display: none;
    }
}
</style>