<template>
    <nav class="navbar">
        <div class="navbar-container">

            <!-- Logo -->
            <a class="navbar-logo" href="/">
                <div class="logo-box student">CC</div>
                <div class="logo-text">
                    <div class="logo-title">CodeClass</div>
                    <small class="logo-subtitle">Learning</small>
                </div>
            </a>

            <!-- Menu items -->
            <ul class="navbar-menu">
                <li class="nav-item">
                    <router-link to="/student" exact class="nav-link">Dashboard</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/student/courses" class="nav-link">My Courses</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/student/course-store" class="nav-link">Course Store</router-link>
                </li>
                <li class="nav-item">
                    <router-link to="/student/profile" class="nav-link">Profile</router-link>
                </li>
            </ul>

            <!-- Search and Right section -->
            <div class="navbar-right">


                <!-- User dropdown -->
                <div class="dropdown">
                    <button class="user-btn" @click.stop="toggleDropdown">
                        <div class="user-avatar">{{ userInitial }}</div>
                        <div class="user-info">
                            <div class="user-name">{{ userName }}</div>
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
            userName: 'Student',
            userRole: 'Student',
        }
    },
    watch: {
        // Watch for route changes to refresh user data
        '$route'() {
            this.loadUser();
        }
    },
    computed: {
        userInitial() {
            const name = this.userName || 'A'
            return name.trim().charAt(0).toUpperCase()
        }
    },
    async mounted() {
        await this.loadUser();
        
        // Listen for profile updates
        window.addEventListener('profileUpdated', this.handleProfileUpdate);
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                this.showDropdown = false;
            }
        });
    },
    beforeUnmount() {
        window.removeEventListener('profileUpdated', this.handleProfileUpdate);
    },
    methods: {
        handleProfileUpdate(event) {
            const profile = event.detail;
            if (profile?.name) {
                this.userName = profile.name;
                console.log('🔄 MenuStudent updated userName from event:', profile.name);
            }
        },
        toggleDropdown(event) {
            event?.stopPropagation();
            this.showDropdown = !this.showDropdown;
        },
        logout() {
            console.log('Logging out...');
            this.showDropdown = false;
            
            // Clear all stored data
            localStorage.removeItem('token');
            localStorage.removeItem('userInfo');
            localStorage.removeItem('session');
            sessionStorage.clear();
            
            // Redirect to login or home
            this.$router.push('/login').catch(() => {
                this.$router.push('/');
            });
        },
        async fetchProfile() {
            try {
                const session = getStoredSession();
                if (!session?.access_token) return;
                
                const axios = (await import('axios')).default;
                const res = await axios.get('http://localhost:5000/api/student/profile', {
                    headers: { Authorization: `Bearer ${session.access_token}` }
                });
                
                console.log('📋 MenuStudent profile response:', res.data);
                
                const st = res.data?.student || {};
                const name = st.name || st.full_name || st.FullName || '';
                if (name) {
                    this.userName = name;
                    console.log('✅ Updated userName to:', name);
                }
                
                // Role from session or default
                const role = session?.user?.role || session?.role || 'student';
                this.userRole = (role || '').charAt(0).toUpperCase() + (role || '').slice(1);
            } catch (e) {
                console.warn('Profile load failed in MenuStudent:', e);
            }
        },
        async loadUser() {
            const session = getStoredSession();
            console.log('🔍 MenuStudent loading user from session:', session);
            
            const u = session?.user || {};
            const name = u.full_name || u.FullName || u.name || u.username;
            
            if (name) {
                this.userName = name;
                console.log('✅ Got name from session:', name);
            } else {
                console.log('📡 No name in session, fetching from backend...');
                // Fallback to backend profile
                await this.fetchProfile();
            }
            
            const role = u.role || session?.role || 'student';
            this.userRole = (role || '').charAt(0).toUpperCase() + (role || '').slice(1);
        },
        
        // Thêm method để refresh data từ bên ngoài
        async refreshUserData() {
            await this.fetchProfile();
        }
    }
};
</script>

<style scoped>
.navbar {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}

.navbar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: inherit;
}

.logo-box {
    width: 40px;
    height: 40px;
    background: #1f2937;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 700;
    font-size: 16px;
}

.logo-box.student {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.logo-text {
    display: flex;
    flex-direction: column;
}

.logo-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.2;
}

.logo-subtitle {
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.navbar-menu {
    display: flex;
    align-items: center;
    gap: 8px;
    list-style: none;
    margin: 0;
    padding: 0;
}

.nav-item {
    position: relative;
}

.nav-link {
    display: block;
    padding: 8px 16px;
    color: #666;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.2s ease;
    position: relative;
}

.nav-link:hover {
    color: #1a1a1a;
    background: #f8f9fa;
}

.nav-link.router-link-exact-active {
    color: #1a1a1a;
    background: #f8f9fa;
}

.nav-link.router-link-exact-active::after {
    content: '';
    position: absolute;
    bottom: -16px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.search-container {
    position: relative;
}

.search-input {
    width: 280px;
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.2s ease;
}

.search-input:focus {
    outline: none;
    border-color: #1f2937;
    box-shadow: 0 0 0 3px rgba(31, 41, 55, 0.1);
}

.notification-btn {
    position: relative;
    padding: 8px 16px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #1a1a1a;
    transition: all 0.2s ease;
}

.notification-btn:hover {
    background: #f8f9fa;
    border-color: #9ca3af;
}

.notification-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    min-width: 20px;
    height: 20px;
    background: #ef4444;
    color: white;
    font-size: 11px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    padding: 0 6px;
}

.dropdown {
    position: relative;
}

.user-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.user-btn:hover {
    background: #f8f9fa;
    border-color: #9ca3af;
}

.user-avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-weight: 600;
    font-size: 14px;
}

.user-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.user-name {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.2;
}

.user-role {
    font-size: 12px;
    color: #666;
}

.dropdown-menu {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-width: 120px;
    list-style: none;
    margin: 0;
    padding: 4px 0;
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
    background: #f8f9fa;
}

.dropdown-menu li a.logout {
    color: #ef4444;
}

.dropdown-menu li a.logout:hover {
    background: #fef2f2;
}

.divider {
    height: 1px;
    background: #e5e7eb;
    margin: 8px 0;
}

@media (max-width: 1024px) {
    .search-input {
        width: 200px;
    }

    .navbar-menu {
        gap: 4px;
    }

    .nav-link {
        padding: 8px 12px;
        font-size: 13px;
    }
}

@media (max-width: 768px) {
    .navbar-container {
        padding: 0 16px;
    }

    .search-container {
        display: none;
    }

    .navbar-menu {
        display: none;
    }
}
</style>
