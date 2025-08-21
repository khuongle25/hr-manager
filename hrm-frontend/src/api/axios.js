import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/", // Đổi nếu backend khác port
  withCredentials: true,
});

// Thêm token vào header cho mọi request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Xử lý token hết hạn
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh");
        if (refreshToken) {
          const response = await axios.post(
            "http://localhost:8000/api/login/refresh/",
            {
              refresh: refreshToken,
            }
          );

          const { access } = response.data;
          localStorage.setItem("access", access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Token refresh thất bại, redirect về login
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
