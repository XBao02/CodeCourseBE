import axios from "axios";
import { getStoredSession } from "./authService";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const http = axios.create({
  baseURL: `${API_BASE_URL}/chat`,
  timeout: 15000,
});

const resolveToken = () => {
  const session = getStoredSession();
  if (session?.access_token) return session.access_token;
  const legacy = localStorage.getItem("token") || sessionStorage.getItem("token");
  if (legacy) return legacy;
  const rawSession = localStorage.getItem("session") || sessionStorage.getItem("session");
  try {
    const parsed = rawSession ? JSON.parse(rawSession) : null;
    return parsed?.access_token || parsed?.token;
  } catch (e) {
    return null;
  }
};

http.interceptors.request.use((config) => {
  const token = resolveToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const fetchThreads = async () => {
  const { data } = await http.get("/threads");
  return data;
};

export const fetchMessages = async ({ courseId, studentId, since } = {}) => {
  if (!courseId) throw new Error("courseId is required");
  const params = { course_id: courseId };
  if (studentId) params.student_id = studentId;
  if (since) params.since = since;
  const { data } = await http.get("/messages", { params });
  return data;
};

export const sendMessage = async ({
  courseId,
  studentId,
  content,
  attachment_url,
  attachment_type,
  attachment_name,
  message_type,
}) => {
  const payload = {
    course_id: courseId,
    content,
    attachment_url,
    attachment_type,
    attachment_name,
    message_type,
  };
  if (studentId) payload.student_id = studentId;
  const { data } = await http.post("/messages", payload);
  return data;
};

export const uploadAttachment = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const { data } = await http.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export default {
  fetchThreads,
  fetchMessages,
  sendMessage,
  uploadAttachment,
};
