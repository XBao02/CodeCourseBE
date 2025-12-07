import { ref, computed, onMounted } from "vue";
import { getStoredSession } from "@/services/authService";
import { getLearningPath } from "@/api/newbie";

export function useNewbiePath() {
  const learningPath = ref(null);
  const loading = ref(true);
  const error = ref(null);

  const session = computed(() => getStoredSession());
  const userId = computed(() => session.value?.user?.id || null);
  const userRole = computed(() => session.value?.user?.role || null);
  const isStudent = computed(() => !!userId.value && userRole.value === "student");
  const resultLink = computed(() =>
    userId.value ? `/newbie/result?userId=${userId.value}` : "/newbie"
  );
  const startLink = computed(() =>
    isStudent.value && userId.value
      ? `/newbie/test?userId=${userId.value}`
      : "/newbie"
  );

  const loadPath = async () => {
    if (!isStudent.value) {
      loading.value = false;
      return;
    }
    try {
      const { data } = await getLearningPath(userId.value);
      learningPath.value = data;
    } catch (err) {
      error.value = err?.response?.data?.error;
    } finally {
      loading.value = false;
    }
  };

  onMounted(loadPath);

  return {
    learningPath,
    loading,
    error,
    isStudent,
    resultLink,
    startLink,
    loadPath,
  };
}
