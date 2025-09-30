<template>
  <div class="register-page">
    <canvas id="matrix"></canvas>

    <div class="register-card">
      <h2 class="register-title">✍️ Create Your Account</h2>
      <p class="register-subtitle">Join CodeClass today</p>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            v-model="username"
            type="text"
            id="username"
            placeholder="your_username"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            v-model="email"
            type="email"
            id="email"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            v-model="password"
            type="password"
            id="password"
            placeholder="********"
            required
          />
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirm Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            id="confirm-password"
            placeholder="********"
            required
          />
        </div>

        <div class="form-check">
          <input type="checkbox" id="terms" v-model="agreedToTerms" required />
          I agree to CodeClass
            <a href="#" class="terms-link">Terms of Service</a> and
            <a href="#" class="terms-link">Privacy Policy</a>.
          
        </div>

        <button type="submit" class="btn-register">Register</button>
      </form>

      <p class="login-link">
        Already have an account?
        <router-link to="/login">Login now</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "Register",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      agreedToTerms: false,
    };
  },
  mounted() {
    this.initMatrix();
  },
  methods: {
    handleRegister() {
      if (this.password !== this.confirmPassword) {
        alert("Passwords do not match!");
        return;
      }
      // Then, check if the user has agreed to the terms
      if (!this.agreedToTerms) {
        alert("You must agree to the Terms of Service and Privacy Policy.");
        return;
      }
      console.log("Registration info:", this.username, this.email, this.password);
    },
    initMatrix() {
      const canvas = document.getElementById("matrix");
      const ctx = canvas.getContext("2d");

      canvas.height = window.innerHeight;
      canvas.width = window.innerWidth;

      const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ";
      const fontSize = 14;
      const columns = canvas.width / fontSize;

      const drops = [];
      for (let x = 0; x < columns; x++) drops[x] = 1;

      function draw() {
        ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00ff99"; // neon green
        ctx.font = fontSize + "px monospace";

        for (let i = 0; i < drops.length; i++) {
          const text = letters[Math.floor(Math.random() * letters.length)];
          ctx.fillText(text, i * fontSize, drops[i] * fontSize);

          if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
          }
          drops[i]++;
        }
      }

      setInterval(draw, 33);

      window.addEventListener("resize", () => {
        canvas.height = window.innerHeight;
        canvas.width = window.innerWidth;
      });
    },
  },
};
</script>

<style scoped>
/* Full page with dark background */
.register-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: "Fira Code", monospace;
}

/* Canvas Matrix */
#matrix {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 0;
  background: black;
}

/* Card */
.register-card {
  position: relative;
  z-index: 1;
  background: rgba(20, 20, 20, 0.85);
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 0 25px rgba(0, 255, 128, 0.4);
  width: 100%;
  max-width: 420px;
  text-align: center;
  border: 1px solid rgba(0, 255, 128, 0.3);
  backdrop-filter: blur(4px);
  animation: fadeIn 1s ease-in-out;
}

/* Title */
.register-title {
  font-size: 26px;
  font-weight: 700;
  color: #00ff99;
  margin-bottom: 8px;
  text-shadow: 0 0 12px rgba(0, 255, 128, 0.8);
}
.register-subtitle {
  font-size: 14px;
  color: #aaa;
  margin-bottom: 25px;
}

/* Inputs */
.form-group {
  margin-bottom: 18px;
  text-align: left;
}
.form-group label {
  font-size: 13px;
  margin-bottom: 6px;
  display: block;
  color: #00ff99;
}
.form-group input {
  width: 100%;
  padding: 10px 12px;
  background: #111;
  border: 1px solid #333;
  border-radius: 6px;
  font-size: 14px;
  color: #eee;
  outline: none;
  transition: 0.3s;
}
.form-group input:focus {
  border-color: #00ff99;
  box-shadow: 0 0 6px #00ff99;
}

/* Button */
.btn-register {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #00ff99, #00b894);
  color: #111;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.3s;
}
.btn-register:hover {
  background: linear-gradient(135deg, #00b894, #00ff99);
  box-shadow: 0 0 12px #00ff99;
  transform: translateY(-2px);
}

/* Link */
.login-link {
  margin-top: 20px;
  font-size: 14px;
}
.login-link a {
  color: #00ff99;
  font-weight: 600;
  text-decoration: none;
}
.login-link a:hover {
  text-decoration: underline;
}

/* Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>