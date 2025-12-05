<template>
  <div class="auth-page register-theme">

    <div class="auth-shell">
      <div class="auth-card">
        <router-link to="/" class="back-button" title="Back to home">
          <span>←</span>
        </router-link>

        <section class="card-form">
          <header>
            <p class="eyebrow subtle">Create account</p>
            <h2>{{ step === 1 ? 'Unlock your next chapter' : 'Verify your email' }}</h2>
            <p class="subtitle">
              {{ step === 1 
                ? 'Join the student space and sync progress across every device.' 
                : `We've sent a verification code to ${email}` 
              }}
            </p>
          </header>

          <!-- Step 1: Registration Form -->
          <form v-if="step === 1" @submit.prevent="handleSendOTP">
            <label class="field">
              <span>Full name</span>
              <input
                v-model="username"
                type="text"
                placeholder="Nguyen Van A"
                required
              />
            </label>

            <label class="field">
              <span>Email</span>
              <input
                v-model="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </label>

            <div class="field-row">
              <label class="field">
                <span>Password</span>
                <input
                  v-model="password"
                  type="password"
                  placeholder="Minimum 6 characters"
                  required
                />
              </label>
              <label class="field">
                <span>Confirm password</span>
                <input
                  v-model="confirmPassword"
                  type="password"
                  placeholder="Repeat password"
                  required
                />
              </label>
            </div>

            <p v-if="errorMessage" class="banner error" role="alert">
              {{ errorMessage }}
            </p>
            <p v-if="successMessage" class="banner success" role="status">
              {{ successMessage }}
            </p>

            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? "Sending..." : "SEND VERIFICATION CODE" }}
            </button>
          </form>

          <!-- Step 2: OTP Verification Form -->
          <form v-else @submit.prevent="handleVerifyAndRegister">
            <label class="field">
              <span>Verification Code</span>
              <input
                v-model="otpCode"
                type="text"
                placeholder="Enter 6-digit code"
                maxlength="6"
                pattern="[0-9]{6}"
                required
                autofocus
              />
              <span class="field-hint">Check your email inbox (and spam folder)</span>
            </label>

            <p v-if="errorMessage" class="banner error" role="alert">
              {{ errorMessage }}
            </p>
            <p v-if="successMessage" class="banner success" role="status">
              {{ successMessage }}
            </p>

            <div class="button-row">
              <button type="button" class="btn-secondary" @click="goBackToStep1" :disabled="isSubmitting">
                ← Back
              </button>
              <button type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? "Verifying..." : "VERIFY & REGISTER" }}
              </button>
            </div>

            <div class="resend-section">
              <button type="button" class="btn-link" @click="handleResendOTP" :disabled="resendCooldown > 0">
                {{ resendCooldown > 0 ? `Resend code (${resendCooldown}s)` : 'Resend verification code' }}
              </button>
            </div>
          </form>

          <footer>
            Already have an account?
            <router-link to="/login" class="inline-link">Sign in</router-link>
          </footer>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import {
  registerUser,
  persistSession,
  getRoleLandingPath,
} from "../../services/authService";
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api/auth';

export default {
  name: "Register",
  data() {
    return {
      step: 1, // 1 = Registration form, 2 = OTP verification
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      otpCode: "",
      isSubmitting: false,
      errorMessage: "",
      successMessage: "",
      resendCooldown: 0,
      resendTimer: null,
    };
  },
  methods: {
    async handleSendOTP() {
      this.errorMessage = "";
      this.successMessage = "";

      const trimmedName = this.username.trim();
      const trimmedEmail = this.email.trim().toLowerCase();

      if (!trimmedName) {
        this.errorMessage = "Please provide your full name.";
        return;
      }

      if (!trimmedEmail) {
        this.errorMessage = "Please provide your email.";
        return;
      }

      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        return;
      }

      if (this.password.length < 6) {
        this.errorMessage = "Password must be at least 6 characters.";
        return;
      }

      this.isSubmitting = true;
      try {
        const response = await axios.post(`${API_BASE}/send-otp`, {
          email: trimmedEmail
        });

        if (response.data.success) {
          this.successMessage = "Verification code sent! Check your email.";
          setTimeout(() => {
            this.step = 2;
            this.successMessage = "";
            this.startResendCooldown(60); // 60 seconds cooldown
          }, 1500);
        }
      } catch (error) {
        this.errorMessage = error?.response?.data?.error || "Failed to send verification code. Please try again.";
      } finally {
        this.isSubmitting = false;
      }
    },

    async handleVerifyAndRegister() {
      this.errorMessage = "";
      this.successMessage = "";

      if (!this.otpCode || this.otpCode.length !== 6) {
        this.errorMessage = "Please enter the 6-digit verification code.";
        return;
      }

      this.isSubmitting = true;
      const trimmedEmail = this.email.trim().toLowerCase();
      const trimmedName = this.username.trim();
      const defaultRole = "student";

      try {
        // Step 1: Verify OTP
        const verifyResponse = await axios.post(`${API_BASE}/verify-otp`, {
          email: trimmedEmail,
          code: this.otpCode
        });

        if (!verifyResponse.data.success) {
          throw new Error(verifyResponse.data.error || "Verification failed");
        }

        this.successMessage = "Email verified! Creating your account...";

        // Step 2: Register user
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const payload = await registerUser({
          email: trimmedEmail,
          password: this.password,
          full_name: trimmedName,
          role: defaultRole,
        });

        persistSession(payload, true);
        this.successMessage = "Account created successfully! Redirecting...";
        
        const next = payload.nextRoute || getRoleLandingPath(payload.user?.role || defaultRole);
        setTimeout(() => {
          this.$router.push(next || "/");
        }, 1000);

      } catch (error) {
        const errorMsg = error?.response?.data?.error || error.message || "Verification failed. Please try again.";
        this.errorMessage = errorMsg;
        
        // If verification failed, allow user to try again or go back
        if (errorMsg.includes("expired") || errorMsg.includes("attempts")) {
          setTimeout(() => {
            this.goBackToStep1();
          }, 3000);
        }
      } finally {
        this.isSubmitting = false;
      }
    },

    async handleResendOTP() {
      if (this.resendCooldown > 0) return;

      this.errorMessage = "";
      this.successMessage = "";

      try {
        const response = await axios.post(`${API_BASE}/resend-otp`, {
          email: this.email.trim().toLowerCase()
        });

        if (response.data.success) {
          this.successMessage = "New code sent! Check your email.";
          this.startResendCooldown(60);
          setTimeout(() => {
            this.successMessage = "";
          }, 3000);
        }
      } catch (error) {
        this.errorMessage = error?.response?.data?.error || "Failed to resend code.";
      }
    },

    goBackToStep1() {
      this.step = 1;
      this.otpCode = "";
      this.errorMessage = "";
      this.successMessage = "";
      this.clearResendTimer();
    },

    startResendCooldown(seconds) {
      this.resendCooldown = seconds;
      this.clearResendTimer();
      
      this.resendTimer = setInterval(() => {
        this.resendCooldown--;
        if (this.resendCooldown <= 0) {
          this.clearResendTimer();
        }
      }, 1000);
    },

    clearResendTimer() {
      if (this.resendTimer) {
        clearInterval(this.resendTimer);
        this.resendTimer = null;
      }
    }
  },

  beforeUnmount() {
    this.clearResendTimer();
  }
};
</script>

<style scoped>
.auth-page.register-theme {
  background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.background-grid {
  display: none;
}

.glow-ring {
  display: none;
}

.auth-shell {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  padding: 0 20px;
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
  padding: 36px 28px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.card-visual {
  background: none;
  border: none;
  padding-bottom: 0;
}

.card-visual h1,
.card-visual .eyebrow,
.card-visual .subtitle {
  color: #1e293b;
}

.card-form {
  background: none;
  border: none;
  padding-top: 0;
}

.card-form header h2,
.card-form header .eyebrow,
.card-form header .subtitle {
  color: #1e293b;
}

.card-form header h2 {
  font-size: 26px;
  margin: 8px 0 4px 0;
}

.card-form header .eyebrow {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #3b82f6;
  margin: 0;
}

.card-form header .subtitle {
  font-size: 0.9rem;
  margin: 8px 0 24px 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 18px;
}

.field span {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.field input {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #1e293b;
  border-radius: 8px;
  padding: 0.8rem 0.95rem;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.field input::placeholder {
  color: #94a3b8;
}

.field input:focus {
  border-color: #3b82f6;
  background: #ffffff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-hint {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.inline-check {
  display: flex;
  gap: 0.7rem;
  color: #475569;
  font-size: 0.85rem;
  margin: 1.5rem 0;
}

.inline-check input {
  accent-color: #3b82f6;
  cursor: pointer;
}

.inline-check a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.inline-check a:hover {
  text-decoration: underline;
}

.banner {
  border-radius: 8px;
  padding: 0.85rem 0.95rem;
  font-size: 0.85rem;
  border: 1px solid transparent;
  margin-bottom: 18px;
}

.banner.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

.banner.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #16a34a;
}

button[type="submit"] {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.9rem;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.card-form footer {
  color: #2563eb;
  text-align: center;
  font-size: 0.85rem;
}

.inline-link {
  color: #3b82f6;
  font-weight: 600;
}

.inline-link:hover {
  text-decoration: underline;
}

.button-row {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.btn-secondary {
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.9rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #94a3b8;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.resend-section {
  text-align: center;
  margin-top: 12px;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  padding: 8px;
}

.btn-link:hover:not(:disabled) {
  color: #2563eb;
}

.btn-link:disabled {
  color: #94a3b8;
  cursor: not-allowed;
  text-decoration: none;
}

@media (max-width: 960px) {
  .auth-card {
    padding: 24px 12px;
  }
}

.back-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  text-decoration: none;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  margin-bottom: 16px;
}

.back-button:hover {
  background: #e0e7ff;
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateX(-2px);
}
</style>
