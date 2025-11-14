<template>
  <div class="auth-page register-theme">
    <div class="background-grid"></div>
    <div class="glow-ring glow-ring-1"></div>
    <div class="glow-ring glow-ring-2"></div>

    <div class="auth-shell">
      <div class="auth-card">
        <section class="card-visual">
          <p class="eyebrow">CodeCourse Studio</p>
          <h1>Shape the next version of you.</h1>
          <p class="subtitle">
            Clean workspace. Elegant tooling. Classic typography with futuristic flow.
          </p>

          <div class="heritage-list">
            <article>
              <h3>Guided tracks</h3>
              <p>Structured paths that respect your craft and time.</p>
            </article>
            <article>
              <h3>Mentor rooms</h3>
              <p>Feedback loops with people who’ve shipped real products.</p>
            </article>
            <article>
              <h3>Daily rituals</h3>
              <p>Minimal prompts that keep the streak alive.</p>
            </article>
          </div>
        </section>

        <section class="card-form">
          <header>
            <p class="eyebrow subtle">Create account</p>
            <h2>Unlock your next chapter</h2>
            <p class="subtitle">
              Join the student space and sync progress across every device.
            </p>
          </header>

          <form @submit.prevent="handleRegister">
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

            <label class="inline-check">
              <input type="checkbox" v-model="agreedToTerms" />
              <span>
                I agree to the
                <a href="#" target="_blank">Terms of Service</a>
                and
                <a href="#" target="_blank">Privacy Policy</a>.
              </span>
            </label>

            <p v-if="errorMessage" class="banner error" role="alert">
              {{ errorMessage }}
            </p>
            <p v-if="successMessage" class="banner success" role="status">
              {{ successMessage }}
            </p>

            <button type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? "Creating account..." : "Launch student space" }}
            </button>
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

export default {
  name: "Register",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      agreedToTerms: false,
      isSubmitting: false,
      errorMessage: "",
      successMessage: "",
    };
  },
  methods: {
    async handleRegister() {
      this.errorMessage = "";
      this.successMessage = "";

      const trimmedName = this.username.trim();
      const trimmedEmail = this.email.trim().toLowerCase();
      const defaultRole = "student";

      if (!trimmedName) {
        this.errorMessage = "Please provide your full name.";
        return;
      }

      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        return;
      }

      if (!this.agreedToTerms) {
        this.errorMessage = "You must agree to the Terms of Service.";
        return;
      }

      this.isSubmitting = true;
      try {
        const payload = await registerUser({
          email: trimmedEmail,
          password: this.password,
          full_name: trimmedName,
          role: defaultRole,
        });
        persistSession(payload, true);
        this.successMessage = "Account created successfully. Redirecting...";
        setTimeout(() => {
          this.$router.push(getRoleLandingPath(payload.user?.role || defaultRole));
        }, 800);
      } catch (error) {
        this.errorMessage =
          error?.response?.data?.error ||
          "Unable to register. Please try again.";
      } finally {
        this.isSubmitting = false;
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
  background: radial-gradient(circle at 15% 20%, #232742, #090b17 70%);
  overflow: hidden;
  font-family: "Inter", "Space Grotesk", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #f1f5f9;
}

.background-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(transparent 94%, rgba(148, 163, 184, 0.08) 6%), linear-gradient(90deg, transparent 94%, rgba(148, 163, 184, 0.08) 6%);
  background-size: 60px 60px;
  opacity: 0.35;
}

.glow-ring {
  position: absolute;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  filter: blur(45px);
  opacity: 0.7;
}

.glow-ring-1 {
  top: -120px;
  left: 6%;
  background: radial-gradient(circle, rgba(96, 165, 250, 0.3), transparent 65%);
}

.glow-ring-2 {
  bottom: -110px;
  right: 10%;
  background: radial-gradient(circle, rgba(74, 222, 128, 0.28), transparent 65%);
}

.auth-shell {
  width: min(1100px, 100%);
  position: relative;
  z-index: 2;
}

.auth-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  border-radius: 34px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(8, 12, 24, 0.92);
  backdrop-filter: blur(22px);
  box-shadow: 0 40px 90px rgba(8, 11, 23, 0.8);
}

.card-visual {
  padding: 3.25rem;
  border-right: 1px solid rgba(148, 163, 184, 0.15);
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.28), rgba(15, 23, 42, 0.6));
}

.card-visual h1 {
  font-size: clamp(2.2rem, 3.7vw, 3.2rem);
  margin-bottom: 1rem;
}

.card-visual .subtitle {
  color: rgba(226, 232, 240, 0.78);
  margin-bottom: 2.5rem;
  line-height: 1.65;
}

.heritage-list {
  display: flex;
  flex-direction: column;
  gap: 1.3rem;
}

.heritage-list article {
  background: rgba(13, 19, 35, 0.75);
  border-radius: 20px;
  padding: 1rem 1.2rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.heritage-list h3 {
  margin: 0 0 0.35rem;
}

.heritage-list p {
  margin: 0;
  color: rgba(226, 232, 240, 0.7);
  font-size: 0.95rem;
}

.card-form {
  padding: 3.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.7rem;
}

.card-form .subtitle {
  color: rgba(226, 232, 240, 0.75);
  margin: 0;
}

.card-form form {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.85);
}

.field input {
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: rgba(15, 23, 42, 0.85);
  padding: 0.95rem 1.15rem;
  color: #f8fafc;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field input:focus {
  border-color: #60a5fa;
  outline: none;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.25);
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.inline-check {
  display: flex;
  gap: 0.7rem;
  color: rgba(226, 232, 240, 0.75);
  font-size: 0.85rem;
}

.inline-check input {
  accent-color: #60a5fa;
}

.inline-check a {
  color: #60a5fa;
  text-decoration: none;
}

.inline-check a:hover {
  text-decoration: underline;
}

.banner {
  border-radius: 16px;
  padding: 0.95rem 1rem;
  font-size: 0.9rem;
  border: 1px solid transparent;
}

.banner.error {
  background: rgba(248, 113, 113, 0.15);
  border-color: rgba(248, 113, 113, 0.45);
  color: #fecaca;
}

.banner.success {
  background: rgba(74, 222, 128, 0.18);
  border-color: rgba(74, 222, 128, 0.45);
  color: #bbf7d0;
}

button[type="submit"] {
  border: none;
  border-radius: 999px;
  padding: 0.95rem;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  background: linear-gradient(120deg, #60a5fa, #34d399);
  box-shadow: 0 18px 38px rgba(20, 83, 45, 0.45);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

button[type="submit"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 24px 42px rgba(20, 83, 45, 0.55);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.card-form footer {
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.8);
}

.inline-link {
  color: #60a5fa;
  text-decoration: none;
}

.inline-link:hover {
  text-decoration: underline;
}

@media (max-width: 960px) {
  .auth-card {
    grid-template-columns: 1fr;
  }

  .card-visual {
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  }
}
</style>
