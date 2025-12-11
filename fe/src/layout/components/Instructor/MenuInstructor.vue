<template>
    <nav class="navbar">
        <div class="navbar-container">

            <a class="navbar-logo" href="/">
                <div class="logo-box">CC</div>
                <div class="logo-text">
                    <div class="logo-title">CodeClass</div>
                    <small class="logo-subtitle">Manager</small>
                </div>
            </a>

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
            </ul>

            <div class="navbar-right">
                <div class="dropdown" ref="dropdownRef">
                    <button class="user-btn" @click.stop="toggleDropdown">
                        <div class="user-avatar">{{ userInitial }}</div>
                        <div class="user-info">
                            <div class="user-name">{{ instructorName }}</div>
                            <small class="user-role">{{ userRole }}</small>
                        </div>
                    </button>
                    
                    <ul v-show="showDropdown" class="dropdown-menu">
                        <li><a href="#" @click.prevent="logout" class="logout">Logout</a></li>
                    </ul>
                </div>
            </div>

        </div>
    </nav>
</template>

<script>
import { getStoredSession } from '../../../services/authService'

export default {
    data() {
        return {
            showDropdown: false,
            instructorName: 'Instructor',
            userRole: 'Instructor'
        }
    },
    computed: {
        userInitial() {
            const name = this.instructorName || 'I'
            return name.trim().charAt(0).toUpperCase()
        }
    },
    async mounted() {
        console.log('🚀 MenuInstructor mounted');
        await this.loadUser();

        // Close dropdown when clicking outside
        document.addEventListener('click', this.handleClickOutside);
        
        console.log('✅ MenuInstructor initialized');
    },
    beforeDestroy() {
        // Dọn dẹp event listener khi component bị hủy để tránh lỗi bộ nhớ
        document.removeEventListener('click', this.handleClickOutside);
    },
    methods: {
        handleClickOutside(event) {
            // Kiểm tra xem click có nằm trong dropdown không
            const dropdownElement = this.$refs.dropdownRef;
            if (dropdownElement && !dropdownElement.contains(event.target)) {
                if (this.showDropdown) {
                    console.log('🔽 Closing dropdown (clicked outside)');
                    this.showDropdown = false;
                }
            }
        },
        toggleDropdown() {
            console.log('🔘 toggleDropdown clicked!');
            this.showDropdown = !this.showDropdown;
        },
        goToSettings() {
            console.log('⚙️ goToSettings clicked');
            this.showDropdown = false;
            this.$router.push('/instructor/settings');
        },
        logout() {
            console.log('🚪 Logging out instructor...');
            this.showDropdown = false;
            
            localStorage.removeItem('token');
            localStorage.removeItem('userInfo');
            localStorage.removeItem('session');
            sessionStorage.clear();
            
            this.$router.push('/login').catch(() => {
                this.$router.push('/');
            });
        },
        async fetchProfile() {
            try {
                const session = getStoredSession();
                if (!session?.access_token) return;
                
                const axios = (await import('axios')).default;
                const res = await axios.get('http://localhost:5000/api/instructor/profile', {
                    headers: { Authorization: `Bearer ${session.access_token}` }
                });
                
                const name = res.data?.full_name || res.data?.username || '';
                if (name) {
                    this.instructorName = name;
                }
                
                const role = session?.user?.role || session?.role || 'instructor';
                this.userRole = (role || '').charAt(0).toUpperCase() + (role || '').slice(1);
            } catch (e) {
                console.warn('Profile load failed:', e);
            }
        },
        async loadUser() {
            const session = getStoredSession();
            const u = session?.user || {};
            const name = u.full_name || u.FullName || u.name || u.username;
            
            if (name) {
                this.instructorName = name;
            } else {
                await this.fetchProfile();
            }
            
            const role = u.role || session?.role || 'instructor';
            this.userRole = (role || '').charAt(0).toUpperCase() + (role || '').slice(1);
        }
    }
};
</script>

<style scoped>
.navbar {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    /* --- SỬA LỖI TẠI ĐÂY --- */
    position: relative;  /* Bắt buộc phải có để z-index hoạt động */
    z-index: 1000;       /* Đảm bảo navbar nằm trên nội dung trang */
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

/* Dropdown Styles */
.dropdown {
    position: relative;
    /* Loại bỏ overflow hidden nếu có ở các thẻ cha */
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
    width: 100%; /* Đảm bảo nút nhận full click area */
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
    flex-shrink: 0;
}

.user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
    text-align: left;
}

.user-name {
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
    white-space: nowrap;
}

.user-role {
    font-size: 12px;
    color: #999;
    margin: 0;
}

.dropdown-menu {
    position: absolute;
    top: calc(100% + 8px); /* Cách nút một chút */
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    min-width: 180px;
    list-style: none;
    margin: 0;
    padding: 6px 0;
    z-index: 9999;
    display: block;
}

.dropdown-menu li a {
    display: block;
    padding: 10px 16px;
    color: #1a1a1a;
    text-decoration: none;
    font-size: 14px;
    transition: background 0.2s ease;
}

.dropdown-menu li a:hover {
    background: #f3f4f6;
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
    .navbar-menu { gap: 20px; }
}

@media (max-width: 768px) {
    .navbar-container {
        padding: 0 16px;
        height: 60px;
        gap: 12px;
    }
    .navbar-menu { display: none; }
    .logo-subtitle { display: none; }
}
</style>