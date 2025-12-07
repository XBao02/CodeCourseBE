<!-- File: src/components/Student/NewbiePathCard.vue -->
<template>
  <div v-if="isStudent" class="newbie-card" aria-live="polite">
    <div v-if="learningPath" class="newbie-card__content">
      <div>
        <p class="label">Lộ trình AI cá nhân</p>
        <h5>{{ learningPath.recommended_course.title }}</h5>
      </div>
      <p class="meta">
        {{ learningPath.recommended_course.track }} · {{ learningPath.recommended_course.level }}
      </p>
      <p class="description">{{ learningPath.recommended_course.description }}</p>
      <router-link :to="resultLink" class="btn-link">Xem chi tiết lộ trình</router-link>
    </div>
    <div v-else class="newbie-card__content newbie-card__empty">
      <p class="label">Chưa có lộ trình</p>
      <p>Hoàn thành bài test đầu vào để AI gợi ý khóa học + lộ trình phù hợp.</p>
      <router-link :to="startLink" class="btn-link">Bắt đầu bài test</router-link>
    </div>
  </div>
</template>

<script setup>
import { useNewbiePath } from "@/composables/useNewbiePath";

const { learningPath, isStudent, resultLink, startLink } = useNewbiePath();
</script>

<style scoped>
.newbie-card {
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}
.newbie-card__content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.label {
  color: #2563eb;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
}
.meta {
  color: #475569;
  font-size: 0.85rem;
  margin-bottom: 6px;
}
.description {
  font-size: 0.95rem;
  color: #1f2937;
}
.btn-link {
  align-self: flex-start;
  margin-top: 6px;
  font-weight: 600;
  color: #1d4ed8;
}
.newbie-card__empty {
  color: #475569;
  font-size: 0.95rem;
}
</style>
