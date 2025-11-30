<template>
  <div class="auth-page login-theme">
    <div class="auth-shell">
      <div class="auth-card">
        <router-link to="/login" class="back-button" title="Back to login">
          <span>←</span>
        </router-link>
        <section class="card-form">
          <header>
            <p class="eyebrow subtle">Password reset</p>
            <h2>Forgot password</h2>
            <p class="subtitle">Enter your email to receive a reset link</p>
          </header>
          <form @submit.prevent="submit">
            <label class="field">
              <span>Email</span>
              <input v-model="email" type="email" placeholder="you@example.com" required />
            </label>
            <p v-if="errorMessage" class="banner error" role="alert">{{ errorMessage }}</p>
            <p v-if="successMessage" class="banner success" role="status">{{ successMessage }}</p>
            <button type="submit" :disabled="isSubmitting">{{ isSubmitting ? 'Sending...' : 'Send reset link' }}</button>
          </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ForgotPassword',
  data(){
    return { email:'', isSubmitting:false, errorMessage:'', successMessage:'' }
  },
  methods: {
    async submit(){
      this.errorMessage=''; this.successMessage='';
      if(!this.email){ this.errorMessage='Please enter your email.'; return }
      this.isSubmitting = true
      try{
        const res = await axios.post('http://localhost:5000/api/auth/forgot-password', { email: this.email.trim().toLowerCase() })
        if(res.data?.success){
          // For testing, backend may return resetLink
          const link = res.data?.resetLink
          this.successMessage = link ? `Reset link: ${link}` : 'If the email exists, a reset link has been sent.'
        } else {
          this.errorMessage = res.data?.error || 'Failed to request reset.'
        }
      } catch(e){
        this.errorMessage = e?.response?.data?.error || 'Server error'
      } finally { this.isSubmitting = false }
    }
  }
}
</script>

<style scoped>
/* Reuse login styles; minimal overrides */
.auth-shell{ width:100%; max-width:480px; margin:0 auto; }
.auth-card{ background:#fff; border-radius:16px; box-shadow:0 8px 32px rgba(37,99,235,.15); padding:40px 32px; }
.field{ display:flex; flex-direction:column; gap:.45rem; margin-bottom:1rem; }
.banner.error{ background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.3); color:#dc2626; padding:.9rem; border-radius:8px; }
.banner.success{ background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.3); color:#065f46; padding:.9rem; border-radius:8px; }
button[type="submit"]{ width:100%; background:linear-gradient(135deg,#2563eb,#1d4ed8); color:#fff; border:none; border-radius:8px; padding:.95rem; font-weight:600; }
.back-button{ display:inline-flex; align-items:center; justify-content:center; width:40px; height:40px; border-radius:8px; background:#e9eff5; border:1px solid #b0bfcc; color:#0f172a; text-decoration:none; font-size:1.2rem; margin-bottom:16px; }
</style>
