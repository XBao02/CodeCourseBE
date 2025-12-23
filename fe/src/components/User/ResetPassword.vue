<template>
    <div class="reset-password-page">
        <div class="reset-container">
            <div class="reset-card">
                <!-- Back Button -->
                <button @click="goBack" class="back-button">
                    ←
                </button>

                <!-- Header -->
                <div class="header">
                    <h2 class="sign-in-label">Reset Password</h2>
                    <h1>Create New Password</h1>
                    <p class="subtitle">Use your CodeCourse account</p>
                </div>

                <!-- Success Message -->
                <div v-if="showSuccess" class="alert alert-success">
                    <strong>Password Reset Successfully!</strong>
                    <p>Redirecting to login page...</p>
                </div>

                <!-- Error Message -->
                <div v-if="errorMessage" class="alert alert-error">
                    <strong>Error</strong>
                    <p>{{ errorMessage }}</p>
                </div>

                <!-- Form -->
                <form v-if="!showSuccess" @submit.prevent="handleSubmit" class="reset-form">
                    <div class="form-group">
                        <label for="newPassword">New Password</label>
                        <input
                            id="newPassword"
                            v-model="newPassword"
                            :type="showPassword ? 'text' : 'password'"
                            placeholder="Enter new password"
                            required
                            minlength="6"
                            class="form-control"
                            :disabled="isLoading"
                        />
                        <small class="help-text">Password must be at least 6 characters</small>
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword">Confirm Password</label>
                        <input
                            id="confirmPassword"
                            v-model="confirmPassword"
                            :type="showConfirmPassword ? 'text' : 'password'"
                            placeholder="Confirm new password"
                            required
                            minlength="6"
                            class="form-control"
                            :disabled="isLoading"
                        />
                    </div>

                    <!-- Password Mismatch Warning -->
                    <div v-if="passwordMismatch" class="warning-text">
                        ⚠️ Passwords do not match
                    </div>

                    <button
                        type="submit"
                        class="btn-submit"
                        :disabled="isLoading || passwordMismatch || !newPassword || !confirmPassword"
                    >
                        <span v-if="isLoading">RESETTING...</span>
                        <span v-else>RESET PASSWORD</span>
                    </button>
                </form>

                <!-- Footer Links -->
                <div class="footer-links">
                    <router-link to="/login" class="link">Back to Login</router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'ResetPassword',
    data() {
        return {
            token: '',
            newPassword: '',
            confirmPassword: '',
            showPassword: false,
            showConfirmPassword: false,
            isLoading: false,
            showSuccess: false,
            errorMessage: ''
        };
    },
    computed: {
        passwordMismatch() {
            return this.confirmPassword && this.newPassword !== this.confirmPassword;
        }
    },
    mounted() {
        // Get token from URL query parameter
        this.token = this.$route.query.token;
        
        console.log('🔐 Reset Password Page Loaded');
        console.log('   Token:', this.token ? '***' + this.token.slice(-10) : 'NOT FOUND');
        
        if (!this.token) {
            this.errorMessage = 'Invalid reset link. Token not found.';
        }
    },
    methods: {
        goBack() {
            this.$router.go(-1);
        },
        async handleSubmit() {
            // Validate passwords match
            if (this.newPassword !== this.confirmPassword) {
                this.errorMessage = 'Passwords do not match';
                return;
            }

            // Validate password length
            if (this.newPassword.length < 6) {
                this.errorMessage = 'Password must be at least 6 characters';
                return;
            }

            // Check token exists
            if (!this.token) {
                this.errorMessage = 'Invalid reset link. Token not found.';
                return;
            }

            this.isLoading = true;
            this.errorMessage = '';

            try {
                console.log('📤 Sending reset password request...');
                
                const response = await axios.post('http://localhost:5000/api/auth/reset-password', {
                    token: this.token,
                    newPassword: this.newPassword
                });

                console.log('📥 Response:', response.data);

                if (response.data.success) {
                    this.showSuccess = true;
                    console.log('✅ Password reset successful!');
                    
                    // Redirect to login after 2 seconds
                    setTimeout(() => {
                        this.$router.push('/login');
                    }, 2000);
                } else {
                    this.errorMessage = response.data.error || 'Failed to reset password';
                }
            } catch (error) {
                console.error('❌ Error resetting password:', error);
                
                if (error.response) {
                    // Server responded with error
                    this.errorMessage = error.response.data.error || 'Failed to reset password';
                } else if (error.request) {
                    // No response from server
                    this.errorMessage = 'Cannot connect to server. Please try again.';
                } else {
                    // Other errors
                    this.errorMessage = 'An error occurred. Please try again.';
                }
            } finally {
                this.isLoading = false;
            }
        }
    }
};
</script>

<style scoped>
.reset-password-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #e5e7eb;
    padding: 20px;
}

.reset-container {
    width: 100%;
    max-width: 520px;
}

.reset-card {
    background: white;
    border-radius: 24px;
    padding: 48px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    position: relative;
}

.back-button {
    position: absolute;
    top: 24px;
    left: 24px;
    width: 40px;
    height: 40px;
    border: none;
    background: #f3f4f6;
    border-radius: 8px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    color: #6b7280;
}

.back-button:hover {
    background: #e5e7eb;
    color: #374151;
}

.header {
    margin-bottom: 32px;
    margin-top: 24px;
}

.sign-in-label {
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    margin: 0 0 16px 0;
}

.header h1 {
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 8px 0;
    line-height: 1.2;
}

.subtitle {
    font-size: 16px;
    color: #6b7280;
    margin: 0;
}

.alert {
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 24px;
}

.alert-success {
    background: #d1fae5;
    color: #065f46;
}

.alert-error {
    background: #fee2e2;
    color: #991b1b;
}

.alert strong {
    display: block;
    margin-bottom: 4px;
    font-weight: 600;
}

.alert p {
    margin: 0;
    font-size: 14px;
}

.reset-form {
    margin-bottom: 24px;
}

.form-group {
    margin-bottom: 24px;
}

.form-group label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
}

.form-control {
    width: 100%;
    padding: 14px 16px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.2s ease;
    box-sizing: border-box;
    background: #f9fafb;
    color: #1f2937;
}

.form-control::placeholder {
    color: #9ca3af;
}

.form-control:focus {
    outline: none;
    border-color: #3b82f6;
    background: white;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
    opacity: 0.6;
}

.help-text {
    display: block;
    margin-top: 6px;
    font-size: 13px;
    color: #6b7280;
}

.warning-text {
    color: #dc2626;
    font-size: 14px;
    margin-bottom: 16px;
}

.btn-submit {
    width: 100%;
    padding: 16px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
}

.btn-submit:hover:not(:disabled) {
    background: #1d4ed8;
}

.btn-submit:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.footer-links {
    text-align: center;
    padding-top: 24px;
}

.link {
    color: #3b82f6;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s;
}

.link:hover {
    color: #2563eb;
}

@media (max-width: 640px) {
    .reset-card {
        padding: 32px 24px;
        border-radius: 16px;
    }

    .header h1 {
        font-size: 28px;
    }

    .back-button {
        top: 16px;
        left: 16px;
    }
}
</style>
