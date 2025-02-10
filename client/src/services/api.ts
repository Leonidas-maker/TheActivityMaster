import axios, {
  AxiosInstance,
  AxiosError,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import generateFingerprint from "../fingerprint/Fingerprint";
import {
  secureLoadData,
  secureSaveData,
  secureRemoveData,
} from "./secureStorageService";

// Extended request configuration interface with custom flags
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean; // Flag to avoid infinite loops during token refresh
  skipAuth?: boolean; // Flag to skip attaching the access token
}

const BASE_URL = "http://localhost:8001/api/v1";
axios.defaults.baseURL = BASE_URL;

const axiosInstance: AxiosInstance = axios.create();

// Request interceptor: adds fingerprint and attaches access token if skipAuth is not set
axiosInstance.interceptors.request.use(
  async (
    config: InternalAxiosRequestConfig
  ): Promise<InternalAxiosRequestConfig> => {
    config.headers = config.headers || {};
    const customConfig = config as CustomAxiosRequestConfig;

    try {
      const fingerprint = await generateFingerprint();
      if (fingerprint) {
        customConfig.headers["application-id"] = fingerprint;
      }

      // Attach access token if skipAuth is not true
      if (!customConfig.skipAuth) {
        const access_token = await secureLoadData("access_token");
        if (access_token) {
          customConfig.headers["Authorization"] = `Bearer ${access_token}`;
        }
      }
    } catch (error) {
      console.error("Error generating fingerprint:", error);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Variables to handle refresh token process
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

// Process queued requests after token refresh attempt
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor: handles 401 errors and performs token refresh when needed
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;
    // Check if error is a 401 and if the request has not been retried
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      // If refresh is already in progress, queue the request
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token: string) => {
            originalRequest.headers["Authorization"] = "Bearer " + token;
            return axiosInstance(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      const refresh_token = await secureLoadData("refresh_token");

      if (!refresh_token) {
        return Promise.reject(error);
      }

      const fingerprint = await generateFingerprint();

      return new Promise((resolve, reject) => {
        // Use axiosInstance for the refresh token request and set skipAuth to bypass the expired token attachment
        axios
          .post(
            "/auth/refresh-token",
            {},
            { headers: { "application-id": fingerprint, "Authorization": "Bearer " + refresh_token } }
          )
          .then(async ({ data }) => {
            // Adjust these keys based on your API response
            const newAccessToken = data.access_token;
            const newRefreshToken = data.refresh_token;

            // Save new tokens securely
            await secureSaveData("access_token", newAccessToken);
            await secureSaveData("refresh_token", newRefreshToken);

            // Process queued requests with the new token
            processQueue(null, newAccessToken);
            resolve(axiosInstance(originalRequest));
          })
          .catch(async (err) => {
            processQueue(err, null);
            // Clear tokens from storage if refresh fails
            await secureRemoveData("access_token");
            await secureRemoveData("refresh_token");
            reject(err);
          })
          .finally(() => {
            isRefreshing = false;
          });
      });
    }

    return Promise.reject(error);
  }
);

export { axiosInstance, BASE_URL };
