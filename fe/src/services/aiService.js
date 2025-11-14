import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";
const API_ORIGIN = new URL(API_BASE_URL, "http://localhost").origin;

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchAiCourses = async () => {
  const { data } = await client.get("/ai/courses");
  return data?.courses ?? [];
};

export const sendChatMessage = async (prompt, model) => {
  const payload = { prompt };
  if (model) {
    payload.model = model;
  }
  const { data } = await client.post("/ai/chat", payload);
  return data;
};

export const uploadAttachment = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post("/ai/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  const resolvedUrl = data?.url && data.url.startsWith("http")
    ? data.url
    : data?.url
    ? `${API_ORIGIN}${data.url}`
    : '';
  return { ...data, url: resolvedUrl };
};

export const fetchAiModels = async () => {
  const { data } = await client.get("/ai/models");
  return data?.models ?? [];
};

export default {
  fetchAiCourses,
  sendChatMessage,
  fetchAiModels,
  uploadAttachment,
};
