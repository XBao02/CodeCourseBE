<template>
  <div class="auth-page login-theme">
    <div class="background-grid"></div>
    <div class="glow-ring glow-ring-1"></div>
    <div class="glow-ring glow-ring-2"></div>

    <div class="auth-shell">
      <div class="auth-card">
        <router-link to="/" class="back-button" title="Back to home">
          <span>←</span>
        </router-link>

        <section class="card-form">
          <header>
            <p class="eyebrow subtle">Sign in</p>
            <h2>Access your studio</h2>
            <p class="subtitle">Use your CodeCourse account</p>
          </header>

          <form @submit.prevent="handleLogin">
            <label class="field">
              <span>Email</span>
              <input
                v-model="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </label>

            <label class="field">
              <span>Password</span>
              <input
                v-model="password"
                type="password"
                placeholder="••••••••"
                required
              />
              <router-link to="/forgot-password" class="inline-link">
                Forgot password?
              </router-link>
            </label>

            <p v-if="errorMessage" class="banner error" role="alert">
              {{ errorMessage }}
            </p>

            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? "Logging in..." : "LOGIN" }}
            </button>

          </form>

          <footer>
            <router-link to="/register" class="inline-link">Create account</router-link>
          </footer>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import {
  loginUser,
  persistSession,
  getRoleLandingPath,
  getStoredSession,
} from "../../services/authService";

export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
      rememberMe: false,
      isSubmitting: false,
      errorMessage: "",
      isFaceChecking: false,
    };
  },
  mounted() {
    this.prefillFromSession();
  },
  methods: {
    async handleLogin() {
      this.errorMessage = "";
      if (!this.email || !this.password) {
        this.errorMessage = "Please provide both email and password.";
        return;
      }

      this.isSubmitting = true;
      try {
        const payload = await loginUser({
          email: this.email.trim().toLowerCase(),
          password: this.password,
        });
        persistSession(payload, this.rememberMe);
        // Prefer backend-provided nextRoute; fallback to role mapping
        const next = payload.nextRoute || getRoleLandingPath(payload.user?.role);
        this.$router.push(next || "/");
      } catch (error) {
        this.errorMessage =
          error?.response?.data?.error ||
          "Unable to login. Please check your credentials.";
      } finally {
        this.isSubmitting = false;
      }
    },
    prefillFromSession() {
      const session = getStoredSession();
      if (session?.user?.email) {
        this.email = session.user.email;
        this.rememberMe = true;
      }
    },
    async handleFaceLogin() {
      this.errorMessage = "";
      this.isFaceChecking = true;
      try {
        // Placeholder logic – integrate with real FaceID/WebAuthn provider later.
        await new Promise((resolve) => setTimeout(resolve, 1200));
        this.errorMessage = "Face login is not yet connected. Please use email & password.";
      } finally {
        this.isFaceChecking = false;
      }
    },
  },
};
</script>

<style scoped>
.auth-page.login-theme {
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
  max-width: 480px;
  margin: 0 auto;
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(60, 130, 246, 0.08);
  padding: 40px 32px;
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

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 1rem;
}

.field span {
  font-weight: 500;
  color: #1e293b;
}

.field input {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #1e293b;
  border-radius: 8px;
  padding: 0.75rem 1rem;
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

.inline-link {
  color: #3b82f6;
}

.inline-link:hover {
  text-decoration: underline;
}

.inline-check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: #475569;
  margin-bottom: 1.5rem;
}

.inline-check input {
  width: 16px;
  height: 16px;
  accent-color: #3b82f6;
  cursor: pointer;
}

.banner {
  padding: 0.95rem 1.1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  border: 1px solid transparent;
  margin-bottom: 1.5rem;
}

.banner.error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

button[type="submit"] {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.95rem;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 1rem;
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

.secondary-btn {
  width: 100%;
  background: #f1f5f9;
  color: #3b82f6;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.95rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-btn:hover:not(:disabled) {
  background: #e0e7ff;
  border-color: #3b82f6;
  color: #2563eb;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-form footer {
  color: #2563eb;
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
