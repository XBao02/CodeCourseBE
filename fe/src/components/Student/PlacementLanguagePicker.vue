<template>
  <section class="language-picker">
    <header>
      <p class="eyebrow">Placement Test</p>
      <h2>Chọn ngôn ngữ bạn muốn được AI kiểm tra</h2>
      <p class="description">
        Hệ thống sẽ tạo bộ câu hỏi trắc nghiệm phù hợp với lựa chọn của bạn và đánh giá năng lực theo từng kỹ năng.
      </p>
    </header>

    <div v-for="group in languages" :key="group.group" class="language-group">
      <div class="group-heading-row">
        <div class="group-heading">{{ group.group }}</div>
        <div v-if="group.group === 'Programming Languages'" class="level-pills">
          <span class="level-label">Chọn cấp độ:</span>
          <button
            v-for="level in levelOptions"
            :key="level.value"
            type="button"
            class="level-pill"
            :class="{ active: selectedLevel === level.value }"
            @click="selectedLevel = level.value"
          >
            {{ level.label }}
          </button>
        </div>
      </div>
      <div class="language-grid">
        <button
          v-for="item in group.items"
          :key="item.value"
          type="button"
          class="language-card"
          :class="{ active: selectedLanguage === item.value }"
          @click="selectedLanguage = item.value"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <button class="primary" :disabled="!selectedLanguage || loading" @click="startTest">
      {{ loading ? "Đang chuẩn bị câu hỏi..." : "Bắt đầu bài test" }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";
import { getStoredSession } from "@/services/authService";

const languages = [
  {
    group: "Programming Languages",
    items: [
      { value: "python", label: "Python" },
      { value: "java", label: "Java" },
      { value: "javascript", label: "JavaScript" },
      { value: "typescript", label: "TypeScript" },
      { value: "c", label: "C" },
      { value: "cpp", label: "C++" },
      { value: "csharp", label: "C#" },
      { value: "go", label: "Go" },
      { value: "rust", label: "Rust" },
      { value: "php", label: "PHP" },
      { value: "ruby", label: "Ruby" },
      { value: "kotlin", label: "Kotlin" },
      { value: "swift", label: "Swift" },
    ],
  },
  {
    group: "Web / Mobile / Framework",
    items: [
      { value: "web_frontend", label: "Web Frontend" },
      { value: "react", label: "React" },
      { value: "vue", label: "Vue.js" },
      { value: "angular", label: "Angular" },
      { value: "svelte", label: "Svelte" },
      { value: "nodejs", label: "Node.js / Express" },
      { value: "django", label: "Python Django" },
      { value: "flask", label: "Python Flask" },
      { value: "laravel", label: "Laravel (PHP)" },
      { value: "android", label: "Android (Java/Kotlin)" },
      { value: "ios", label: "iOS (Swift)" },
      { value: "flutter", label: "Flutter (Dart)" },
    ],
  },
  {
    group: "Data / ML / DevOps",
    items: [
      { value: "sql", label: "SQL / Database" },
      { value: "machine_learning", label: "Machine Learning" },
      { value: "deep_learning", label: "AI / Deep Learning" },
      { value: "data_analysis", label: "Data Analysis" },
      { value: "devops", label: "DevOps / Docker / CI/CD" },
      { value: "cloud", label: "Cloud (AWS / GCP / Azure)" },
    ],
  },
];

const route = useRoute();
const router = useRouter();
const session = computed(() => getStoredSession());
const levelOptions = [
  { value: "intermediate", label: "Intermediate" },
  { value: "beginner", label: "Beginner" },
  { value: "advanced", label: "Advanced" },
];
const selectedLanguage = ref("");
const selectedLevel = ref(levelOptions[0].value);
const loading = ref(false);
const error = ref("");

const userId = computed(() => Number(route.query.userId) || session.value?.user?.id);

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api",
  timeout: 12000,
});

client.interceptors.request.use((config) => {
  const token = session.value?.access_token;
  if (token && !config.headers?.Authorization) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

const startTest = async () => {
  error.value = "";
  if (!userId.value) {
    error.value = "Vui lòng đăng nhập để làm bài test.";
    return;
  }
  if (!selectedLanguage.value) {
    error.value = "Chọn ngôn ngữ bạn muốn kiểm tra.";
    return;
  }

  loading.value = true;
  try {
    await client.post("/placement/generate-questions", {
      user_id: userId.value,
      language: selectedLanguage.value,
      level: selectedLevel.value,
    });
    router
      .push({
        path: "/student/placement/test",
        query: {
          userId: userId.value,
          language: selectedLanguage.value,
        },
      })
      .catch(() => {});
  } catch (err) {
    error.value = err?.response?.data?.error || "Không tạo được câu hỏi. Vui lòng thử lại.";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.language-picker {
  max-width: 980px;
  margin: 0 auto;
  padding: 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.language-picker header h2 {
  margin: 0;
  font-size: 1.85rem;
}

.language-picker header p {
  margin: 8px 0 0;
  color: #475569;
}

.eyebrow {
  font-size: 0.8rem;
  letter-spacing: 0.3em;
  color: #94a3b8;
  text-transform: uppercase;
  margin: 0 0 4px;
}

.description {
  color: #475569;
  margin-top: 4px;
}

.language-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-heading-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.level-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.level-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.level-pill {
  border: 1px solid transparent;
  border-radius: 999px;
  background: #f1f5f9;
  padding: 6px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
  color: #0f172a;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.level-pill.active {
  background: #e0e7ff;
  border-color: #6366f1;
  color: #1d4ed8;
}

.group-heading {
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.93rem;
}

.language-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 10px;
}

.language-card {
  border: 2px solid transparent;
  border-radius: 14px;
  background: #f8fafc;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  transition: border 0.2s ease, background 0.2s ease;
  min-height: 64px;
}

.language-card.active {
  border-color: #2563eb;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(15, 23, 42, 0.04));
  box-shadow: 0 16px 35px rgba(37, 99, 235, 0.25);
}

.language-card:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

button.primary {
  align-self: flex-start;
  border: none;
  border-radius: 12px;
  padding: 14px 24px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #9333ea);
  cursor: pointer;
  transition: transform 0.2s ease;
  min-width: 220px;
}

button.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button.primary:not(:disabled):hover {
  transform: translateY(-1px);
}

.error {
  color: #dc2626;
  margin: 0;
  font-size: 0.95rem;
}

@media (max-width: 640px) {
  .language-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}
</style>
