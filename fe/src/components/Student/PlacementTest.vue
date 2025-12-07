<template>
  <section class="placement-test">
    <header>
      <h2>Bài test đầu vào</h2>
      <p>Hệ thống sẽ đánh giá năng lực hiện tại qua bộ câu hỏi do AI sinh ra.</p>
      <p class="placement-language">
        Ngôn ngữ đang test: <strong>{{ languageLabel }}</strong>
      </p>
    </header>

    <div v-if="loading" class="status">Đang tải câu hỏi...</div>
    <form v-else @submit.prevent="handleSubmit">
      <div v-for="question in questions" :key="question.id" class="question-card">
        <div class="question-head">
          <span class="skill">{{ question.topic?.toUpperCase() || "GENERAL" }}</span>
          <p>{{ question.question }}</p>
        </div>
        <div class="options">
          <label v-for="option in question.options" :key="option" class="option">
            <input
              type="radio"
              :name="`question-${question.id}`"
              :value="option"
              v-model="answers[question.id]"
            />
            <span>{{ option }}</span>
          </label>
        </div>
      </div>

      <div class="form-footer">
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
        <button type="submit" class="primary" :disabled="submitting">
          {{ submitting ? "Đang gửi kết quả..." : "Hoàn thành bài test" }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";
import { getStoredSession } from "@/services/authService";

const route = useRoute();
const router = useRouter();
const submitting = ref(false);
const error = ref("");
const success = ref("");
const loading = ref(true);
const session = computed(() => getStoredSession());
const userId = computed(() => Number(route.query.userId) || session.value?.user?.id);
const languageMap = {
  python: "Python",
  javascript: "JavaScript",
  cpp: "C++",
  java: "Java",
  web_frontend: "Web Frontend",
  backend: "Backend / API",
};

const languageLabel = computed(() => {
  const raw = (route.query.language || "").toString().trim();
  if (!raw) return "Chưa chọn";
  return languageMap[raw] || raw.replace(/_/g, " ");
});

const questions = ref([]);
const answers = reactive({});

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api",
  timeout: 12000,
});

client.interceptors.request.use((config) => {
  const token = session.value?.access_token;
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const loadQuestions = async () => {
  if (!userId.value) {
    loading.value = false;
    return;
  }
  try {
    const { data } = await client.get(`/placement/questions/latest/${userId.value}`);
    questions.value = data;
  } catch (err) {
    error.value = "Không thể tải câu hỏi. Vui lòng thử lại.";
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  error.value = "";
  success.value = "";
  if (!userId.value) {
    error.value = "Bạn cần đăng nhập để nộp bài.";
    return;
  }
  if (!questions.value.length) {
    error.value = "Chưa có câu hỏi để gửi.";
    return;
  }
  const allAnswered = questions.value.every((q) => answers[q.id]);
  if (!allAnswered) {
    error.value = "Vui lòng trả lời hết các câu hỏi.";
    return;
  }
  submitting.value = true;
  try {
    const payload = questions.value.map((question) => ({
      question_id: question.id,
      chosen_answer: answers[question.id],
    }));
    await client.post("/placement/submit", {
      user_id: userId.value,
      answers: payload,
    });
    success.value = "Kết quả đã được gửi. Hệ thống đang sinh lộ trình.";
    setTimeout(() => router.push("/student"), 1200);
  } catch (err) {
    error.value =
      err?.response?.data?.error || "Không thể gửi kết quả. Vui lòng thử lại.";
  } finally {
    submitting.value = false;
  }
};

watch(userId, () => {
  loading.value = true;
  loadQuestions();
}, { immediate: true });
</script>

<style scoped>
.placement-test {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  padding: 32px;
  border-radius: 18px;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.placement-test header h2 {
  margin: 0;
  font-size: 2rem;
}
.placement-test header p {
  margin: 4px 0 0;
  color: #475569;
}
.placement-language {
  margin: 8px 0 0;
  color: #475569;
  font-weight: 500;
}
.placement-language strong {
  color: #0f172a;
}
.question-card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 18px;
  background: #f9fafc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.question-head {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skill {
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #2563eb;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.option {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  color: #1e293b;
}
.option input {
  accent-color: #2563eb;
}
.form-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
button.primary {
  border: none;
  border-radius: 10px;
  padding: 14px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #9333ea);
  cursor: pointer;
  transition: transform 0.15s ease;
}
button.primary:disabled {
  opacity: 0.6;
  cursor: wait;
}
button.primary:not(:disabled):hover {
  transform: translateY(-2px);
}
.status {
  color: #475569;
  font-weight: 600;
}
.error {
  color: #dc2626;
}
.success {
  color: #059669;
}
</style>
