<template>
  <div class="auth-page login-theme">
    <div class="background-grid"></div>
    <div class="glow-ring glow-ring-1"></div>
    <div class="glow-ring glow-ring-2"></div>

    <div class="auth-shell">
      <div class="auth-card">
        <section class="card-visual">
          <p class="eyebrow">CodeCourse Platform</p>
          <h1>Welcome back, creator.</h1>
          <p class="subtitle">
            Continue the streak, keep sharpening your craft, and sync across all devices.
          </p>

          <ul class="quick-stats">
            <li>
              <span class="value">2k+</span>
              <small>Learners Active</small>
            </li>
            <li>
              <span class="value">98%</span>
              <small>Finish Daily Goals</small>
            </li>
          </ul>
        </section>

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

            <label class="inline-check">
              <input
                type="checkbox"
                v-model="rememberMe"
              />
              <span>Remember me on this device</span>
            </label>

            <p v-if="errorMessage" class="banner error" role="alert">
              {{ errorMessage }}
            </p>

            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? "Logging in..." : "Enter workspace" }}
            </button>

            <div class="divider">
              <span>or</span>
            </div>

            <button
              type="button"
              class="secondary-btn"
              @click="handleFaceLogin"
              :disabled="isSubmitting || isFaceChecking"
            >
              {{ isFaceChecking ? "Scanning..." : "Face ID" }}
            </button>
          </form>

          <footer>
            New here?
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
        const landing = getRoleLandingPath(payload.user?.role);
        this.$router.push(landing);
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
:root {
  color-scheme: dark;
}

.auth-page {
  position: relative;
  min-height: 100vh;
  padding: 4rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top, #1a1f3d, #090b17 65%);
  overflow: hidden;
  font-family: "Inter", "Space Grotesk", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #f1f5f9;
}

.background-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(transparent 95%, rgba(59, 130, 246, 0.08) 5%), linear-gradient(90deg, transparent 95%, rgba(59, 130, 246, 0.08) 5%);
  background-size: 50px 50px;
  opacity: 0.35;
  pointer-events: none;
}

.glow-ring {
  position: absolute;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(74, 222, 128, 0.25), transparent 60%);
  filter: blur(40px);
  opacity: 0.7;
}

.glow-ring-1 {
  top: -120px;
  right: 10%;
}

.glow-ring-2 {
  bottom: -90px;
  left: 5%;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.35), transparent 60%);
}

.auth-shell {
  width: min(1100px, 100%);
  position: relative;
  z-index: 2;
}

.auth-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 0;
  border-radius: 30px;
  overflow: hidden;
  backdrop-filter: blur(18px);
  background: rgba(10, 13, 26, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 30px 90px rgba(15, 23, 42, 0.55);
}

.card-visual {
  padding: 3rem;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.25), rgba(37, 99, 235, 0.05));
  border-right: 1px solid rgba(148, 163, 184, 0.15);
}

.card-visual h1 {
  font-size: clamp(2.25rem, 4vw, 3rem);
  margin-bottom: 1rem;
  color: #f8fafc;
}

.card-visual .subtitle {
  color: rgba(226, 232, 240, 0.75);
  font-size: 0.95rem;
  margin-bottom: 2.25rem;
  line-height: 1.6;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
}

.quick-stats .value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #38bdf8;
}

.quick-stats small {
  color: rgba(226, 232, 240, 0.75);
}

.card-form {
  padding: 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-form header h2 {
  font-size: 1.8rem;
  margin: 0.25rem 0;
}

.card-form .subtitle {
  color: rgba(226, 232, 240, 0.7);
  margin: 0;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.75rem;
  color: #38bdf8;
  margin-bottom: 0.35rem;
}

.eyebrow.subtle {
  color: rgba(148, 163, 184, 0.9);
}

.card-form form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.85);
}

.field input {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 16px;
  padding: 0.95rem 1.15rem;
  color: #f8fafc;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field input:focus {
  border-color: #38bdf8;
  outline: none;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
}

.inline-link {
  font-size: 0.85rem;
  color: #38bdf8;
  text-decoration: none;
  margin-top: 0.35rem;
  display: inline-block;
}

.inline-link:hover {
  text-decoration: underline;
}

.inline-check {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.75);
}

.inline-check input {
  width: 16px;
  height: 16px;
  accent-color: #38bdf8;
}

.banner {
  padding: 0.95rem 1.1rem;
  border-radius: 16px;
  font-size: 0.9rem;
  border: 1px solid transparent;
}

.banner.error {
  background: rgba(248, 113, 113, 0.16);
  border-color: rgba(248, 113, 113, 0.45);
  color: #fecaca;
}

button[type="submit"] {
  width: 100%;
  border: none;
  border-radius: 999px;
  padding: 0.95rem;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  background: linear-gradient(120deg, #38bdf8, #4ade80);
  box-shadow: 0 12px 24px rgba(15, 118, 110, 0.35);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

button[type="submit"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 35px rgba(15, 118, 110, 0.45);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.divider {
  position: relative;
  text-align: center;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.9);
}

.divider::before,
.divider::after {
  content: "";
  position: absolute;
  top: 50%;
  width: 43%;
  height: 1px;
  background: rgba(148, 163, 184, 0.35);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.secondary-btn {
  width: 100%;
  border-radius: 999px;
  padding: 0.95rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: transparent;
  color: #f1f5f9;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, opacity 0.2s ease;
}

.secondary-btn:hover:not(:disabled) {
  border-color: rgba(148, 163, 184, 0.8);
  color: #38bdf8;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-form footer {
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.85);
}

@media (max-width: 960px) {
  .auth-card {
    grid-template-columns: 1fr;
  }

  .card-visual {
    padding-bottom: 2.25rem;
  }

  .card-form {
    padding-top: 2.25rem;
  }
}
</style>
