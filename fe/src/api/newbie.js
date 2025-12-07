// File: src/api/newbie.js
import axios from "axios";
import { getStoredSession } from "@/services/authService";

const client = axios.create({
  baseURL: "http://localhost:5000",
  timeout: 12000,
});

client.interceptors.request.use((config) => {
  const session = getStoredSession();
  const token = session?.access_token;
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function setupNewbieProfile(payload) {
  return client.post("/api/newbie/setup-profile", payload);
}

export async function getTestQuestions(params = {}) {
  return client.get("/api/newbie/test-questions", { params });
}

export async function submitTest(payload) {
  return client.post("/api/newbie/submit-test", payload);
}

export async function requestAiRecommend(userId) {
  return client.post("/api/newbie/ai-recommend", { user_id: userId });
}

export async function getLearningPath(userId) {
  return client.get(`/api/newbie/learning-path/${userId}`);
}

export async function fetchQuizHistory(userId) {
  return client.get(`/api/newbie/history`, {
    params: { user_id: userId },
  });
}
