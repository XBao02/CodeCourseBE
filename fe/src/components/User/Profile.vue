<template>
  <section class="account-page">
    <header class="hero">
      <div>
        <p class="eyebrow">H? so cá nhân</p>
        <h1>Xin chào, {{ profile.name.split(' ')[0] }}</h1>
        <p class="subline">
          C?p nh?t thông tin d? CodeCourse AI d? xu?t l? trình chính xác hon.
        </p>
      </div>
      <button type="button" @click="saveProfile">Luu thay d?i</button>
    </header>

    <div class="grid">
      <article class="panel profile">
        <div class="avatar-ring">
          <img :src="profile.avatar" alt="avatar" />
        </div>
        <h2>{{ profile.name }}</h2>
        <p class="role">{{ profile.role }}</p>
        <p class="headline">{{ profile.headline }}</p>

        <ul class="meta">
          <li>
            <span>Email</span>
            <strong>{{ profile.email }}</strong>
          </li>
          <li>
            <span>Tham gia t?</span>
            <strong>{{ profile.joined }}</strong>
          </li>
        </ul>

        <div class="social">
          <button type="button" v-for="link in social" :key="link.label">
            <i :class="link.icon"></i>
            {{ link.label }}
          </button>
        </div>
      </article>

      <article class="panel form">
        <h3>Thông tin co b?n</h3>
        <div class="form-grid">
          <label>
            H? và tên
            <input v-model="profile.name" type="text" />
          </label>
          <label>
            Email
            <input v-model="profile.email" type="email" />
          </label>
          <label>
            Vai trò
            <select v-model="profile.role">
              <option>Student</option>
              <option>Instructor</option>
              <option>Admin</option>
            </select>
          </label>
          <label>
            Thành ph?
            <input v-model="profile.city" type="text" />
          </label>
          <label class="full">
            Tiêu d? gi?i thi?u
            <textarea v-model="profile.headline" rows="3"></textarea>
          </label>
        </div>
      </article>

      <article class="panel timeline">
        <h3>L? trình h?c t?p</h3>
        <ul>
          <li v-for="item in timeline" :key="item.title">
            <div class="dot"></div>
            <div>
              <p class="title">{{ item.title }}</p>
              <p class="meta">{{ item.time }} · {{ item.status }}</p>
            </div>
            <span class="badge" :class="item.statusClass">{{ item.status }}</span>
          </li>
        </ul>
      </article>

      <article class="panel stats">
        <h3>Ch? s? nhanh</h3>
        <div class="stats-grid">
          <div v-for="stat in stats" :key="stat.label">
            <p>{{ stat.label }}</p>
            <strong>{{ stat.value }}</strong>
            <span>{{ stat.delta }}</span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
export default {
  name: "UserProfile",
  data() {
    return {
      profile: {
        name: "Nguy?n Minh",
        email: "minh.student@example.com",
        role: "Student",
        city: "TP. H? Chí Minh",
        headline: "Front-end developer yêu thích UI c? di?n pha hi?n d?i",
        joined: "03/2024",
        avatar: "https://i.pravatar.cc/160?img=13",
      },
      social: [
        { label: "LinkedIn", icon: "fab fa-linkedin-in" },
        { label: "Github", icon: "fab fa-github" },
        { label: "Behance", icon: "fab fa-behance" },
      ],
      stats: [
        { label: "Khóa dã hoàn thành", value: 8, delta: "+2 tu?n này" },
        { label: "Gi? h?c", value: 126, delta: "+12 gi?" },
        { label: "Ði?m quiz trung bình", value: "92%", delta: "+5%" },
      ],
      timeline: [
        { title: "React Mastery", time: "Hôm nay", status: "Ðang h?c", statusClass: "primary" },
        { title: "Python cho Data", time: "Tu?n tru?c", status: "Ðã hoàn thành", statusClass: "success" },
        { title: "UI/UX Sprint", time: "2 tu?n tru?c", status: "Ch? h?c", statusClass: "neutral" },
      ],
    };
  },
  methods: {
    saveProfile() {
      alert("Ðã luu h? so (mock)");
    },
  },
};
</script>

<style scoped>
.account-page {
  min-height: 100vh;
  padding: 3rem clamp(1.5rem, 5vw, 4rem);
  background: radial-gradient(circle at 10% 10%, #1b1e3a, #060912 70%);
  color: #e2e8f0;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.hero button {
  border: none;
  border-radius: 999px;
  padding: 0.9rem 1.8rem;
  background: linear-gradient(120deg, #60a5fa, #34d399);
  color: #04121f;
  font-weight: 600;
  cursor: pointer;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.75rem;
  color: #60a5fa;
  margin-bottom: 0.5rem;
}

.subline {
  color: rgba(226, 232, 240, 0.75);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.panel {
  border-radius: 28px;
  padding: 1.8rem;
  background: rgba(8, 11, 23, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.profile {
  text-align: center;
}

.avatar-ring {
  width: 140px;
  height: 140px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  padding: 5px;
  background: linear-gradient(120deg, #60a5fa, #34d399);
}

.avatar-ring img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.role {
  color: #38bdf8;
  font-weight: 600;
}

.headline {
  color: rgba(226, 232, 240, 0.75);
  font-size: 0.9rem;
}

.meta {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.meta li {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}

.meta span {
  color: rgba(226, 232, 240, 0.6);
}

.social {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
}

.social button {
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: transparent;
  border-radius: 999px;
  padding: 0.45rem 1rem;
  color: inherit;
  cursor: pointer;
}

.form h3,
.timeline h3,
.stats h3 {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.85);
}

input,
select,
textarea {
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.04);
  padding: 0.65rem 0.85rem;
  color: inherit;
}

.full {
  grid-column: 1 / -1;
}

.timeline ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  align-items: center;
}

.timeline .dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(120deg, #60a5fa, #34d399);
}

.timeline .title {
  font-weight: 600;
  margin: 0;
}

.timeline .meta {
  margin: 0;
  border: none;
  color: rgba(226, 232, 240, 0.65);
}

.badge {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.badge.primary {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.badge.success {
  background: rgba(52, 211, 153, 0.2);
  color: #34d399;
}

.badge.neutral {
  background: rgba(148, 163, 184, 0.2);
  color: rgba(226, 232, 240, 0.8);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.stats-grid div {
  border-radius: 18px;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.stats-grid strong {
  font-size: 1.8rem;
}

.stats-grid span {
  color: #34d399;
}

@media (max-width: 720px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero button {
    width: 100%;
  }
}
</style>
