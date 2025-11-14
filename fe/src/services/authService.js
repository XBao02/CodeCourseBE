import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";
const STORAGE_KEY = "codecourse_auth";
const ROLE_ROUTES = {
  admin: "/admin",
  instructor: "/instructor",
  student: "/student",
};

const fallbackStorageFactory = () => {
  const data = {};
  return {
    getItem(key) {
      return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null;
    },
    setItem(key, value) {
      data[key] = value;
    },
    removeItem(key) {
      delete data[key];
    },
  };
};

const fallbackLocal = fallbackStorageFactory();
const fallbackSession = fallbackStorageFactory();

const getStorageTargets = () => {
  if (typeof window === "undefined") {
    return { local: fallbackLocal, session: fallbackSession };
  }

  return {
    local: window.localStorage || fallbackLocal,
    session: window.sessionStorage || fallbackSession,
  };
};

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

const readRawSession = () => {
  const { local, session } = getStorageTargets();
  return local.getItem(STORAGE_KEY) || session.getItem(STORAGE_KEY);
};

export const getStoredSession = () => {
  const raw = readRawSession();
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    clearSession();
    console.error("Invalid auth session payload", error);
    return null;
  }
};

export const persistSession = (sessionPayload, rememberMe = false) => {
  if (!sessionPayload) {
    return;
  }
  const payload = JSON.stringify(sessionPayload);
  const { local, session } = getStorageTargets();

  if (rememberMe) {
    local.setItem(STORAGE_KEY, payload);
    session.removeItem(STORAGE_KEY);
  } else {
    session.setItem(STORAGE_KEY, payload);
    local.removeItem(STORAGE_KEY);
  }
};

export const clearSession = () => {
  const { local, session } = getStorageTargets();
  local.removeItem(STORAGE_KEY);
  session.removeItem(STORAGE_KEY);
};

http.interceptors.request.use((config) => {
  const currentSession = getStoredSession();
  if (currentSession?.access_token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${currentSession.access_token}`;
  }
  return config;
});

export const loginUser = async ({ email, password }) => {
  const { data } = await http.post("/auth/login", { email, password });
  return data;
};

export const registerUser = async ({ email, password, full_name, role = "student" }) => {
  const { data } = await http.post("/auth/register", {
    email,
    password,
    full_name,
    role,
  });
  return data;
};

export const fetchCurrentUser = async () => {
  const { data } = await http.get("/auth/me");
  return data;
};

export const getRoleLandingPath = (role) => ROLE_ROUTES[role] || "/";

export default {
  loginUser,
  registerUser,
  fetchCurrentUser,
  persistSession,
  getStoredSession,
  clearSession,
  getRoleLandingPath,
};
