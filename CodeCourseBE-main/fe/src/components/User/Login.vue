<template>
  <div class="login-page">
    <!-- Matrix Background -->
    <canvas id="matrix"></canvas>

    <!-- Login Card -->
    <div class="login-card">
      <h2 class="login-title">👨‍💻 CodeClass Login</h2>
      <p class="login-subtitle">Sign in to continue learning</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Email -->
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

        <!-- Password -->
        <div class="form-group">
          <label for="password">Password</label>
          <input
            v-model="password"
            type="password"
            id="password"
            placeholder="********"
            required
          />
          <router-link to="/forgot-password" class="forgot-password-link">Forgot password?</router-link>
        </div>

        <div class="form-check mb-4">
            <input class="form-check-input" type="checkbox" id="rememberMe" v-model="rememberMe">
            <label class="form-check-label" for="rememberMe">
              Remember me
            </label>
          </div>

        <!-- Submit -->
        <button type="submit" class="btn-login">Login</button>
      </form>

      <p class="register-link">
        Don't have an account?
        <router-link to="/register">Register now</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
    };
  },
  mounted() {
    this.initMatrix();
  },
  methods: {
    handleLogin() {
      console.log("Login info:", this.email, this.password);
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

      // resize event
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
.login-page {
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
.login-card {
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
.login-title {
  font-size: 26px;
  font-weight: 700;
  color: #00ff99;
  margin-bottom: 8px;
  text-shadow: 0 0 12px rgba(0, 255, 128, 0.8);
}
.login-subtitle {
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
.btn-login {
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
.btn-login:hover {
  background: linear-gradient(135deg, #00b894, #00ff99);
  box-shadow: 0 0 12px #00ff99;
  transform: translateY(-2px);
}

/* Link */
.register-link {
  margin-top: 20px;
  font-size: 14px;
}
.register-link a {
  color: #00ff99;
  font-weight: 600;
  text-decoration: none;
}
.register-link a:hover {
  text-decoration: underline;
}

/* Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}


</style>
