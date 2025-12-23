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

const languageLabel = computed(() => {
  const raw = (sessionStorage.getItem("placementLanguage") || "").toString().trim();
  if (!raw) return "Chưa chọn";
  return raw.replace(/_/g, " ");
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

const loadQuestions = () => {
  const stored = sessionStorage.getItem("placementQuestions");
  if (!stored) {
    error.value = "Chưa có bộ câu hỏi. Vui lòng chọn ngôn ngữ trước.";
    loading.value = false;
    return;
  }
  try {
    questions.value = JSON.parse(stored) || [];
  } catch (err) {
    questions.value = [];
    error.value = "Lỗi đọc bộ câu hỏi. Vui lòng thử lại.";
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  error.value = "";
  success.value = "";
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
    const payloadAnswers = questions.value.map((question) => ({
      question_id: question.id,
      answer: answers[question.id],
    }));
    const language = sessionStorage.getItem("placementLanguage") || "general";
    const goal = sessionStorage.getItem("placementGoal") || "beginner";
    const batch_id = sessionStorage.getItem("placementBatch") || "";
    const userId = session.value?.user?.id;

    const { data } = await client.post("/placement/run", {
      language,
      goal,
      user_id: userId,
      batch_id,
      answers: payloadAnswers,
    });
    // Persist recommended courses for Skill profile view
    sessionStorage.setItem("placementRecommended", JSON.stringify(data.recommended_courses || []));
    sessionStorage.setItem("placementLevel", data.level || "");
    success.value = `Điểm: ${data.score}. Level: ${data.level}.`;
    sessionStorage.removeItem("placementQuestions");
    setTimeout(() => router.push("/student"), 1500);
  } catch (err) {
    error.value =
      err?.response?.data?.error || "Không thể gửi kết quả. Vui lòng thử lại.";
  } finally {
    submitting.value = false;
  }
};

watch(
  () => route.fullPath,
  () => {
    loading.value = true;
    loadQuestions();
  },
  { immediate: true }
);
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
