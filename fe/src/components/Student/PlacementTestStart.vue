<template>
  <section class="placement-start">
    <header>
      <h2>{{ hasAttempt ? "Làm lại bài test" : "Bắt đầu bài test đầu vào" }}</h2>
      <p>Hệ thống đánh giá logic, lập trình, OOP và Web; chọn ngôn ngữ để AI sinh đề.</p>
    </header>
    <button class="primary" :disabled="loading" @click="startTest">
      {{ loading ? "Đang chuyển..." : hasAttempt ? "Làm lại bài test" : "Bắt đầu bài test" }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { getStoredSession } from "@/services/authService";

const router = useRouter();
const session = computed(() => getStoredSession());
const userId = computed(() => session.value?.user?.id || null);
const loading = ref(false);
const error = ref("");
const hasAttempt = ref(!!session.value?.user?.lastPlacementTestId);

const startTest = async () => {
  error.value = "";
  if (!userId.value) {
    error.value = "Vui lòng đăng nhập trước khi làm bài test.";
    return;
  }
  loading.value = true;
  try {
    router
      .push({
        path: "/student/placement/select-language",
        query: { userId: userId.value },
      })
      .catch(() => {});
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.placement-start {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
  max-width: 520px;
  margin: 0 auto 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.placement-start h2 {
  margin: 0;
  font-size: 1.75rem;
}
.placement-start p {
  margin: 0;
  color: #475569;
  line-height: 1.5;
}
button.primary {
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #9333ea);
  cursor: pointer;
  transition: transform 0.2s ease;
}
button.primary:disabled {
  opacity: 0.6;
  cursor: wait;
}
button.primary:not(:disabled):hover {
  transform: translateY(-1px);
}
.error {
  color: #dc2626;
  font-size: 0.95rem;
  margin: 0;
}
</style>
