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
// Import the imperative router from expo-router.
// Do not use the useRouter hook here because this file is not a React component.
import { router } from "expo-router";
import { asyncRemoveData } from "./asyncStorageService";
import { getGlobalLogout } from "../provider/AuthContextProvider";
import { triggerPermissionRefresh } from "../permissions/PermissionRefreshHandler";

// Extended request configuration interface with custom flags
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean; // Flag to avoid infinite loops during token refresh
  _retry403?: boolean; // Counter for 403 errors
  skipAuth?: boolean; // Flag to skip attaching the access token
}

//! For Android testing replace localhost with your local IP address
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
// Variables to handle permissions refresh process for 403 errors
let isRefreshingPermissions = false;
let failedPermissionQueue: Array<{
  resolve: (shouldRetry: boolean) => void;
  reject: (error: any) => void;
}> = [];
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

// Response interceptor: handles 401 errors and performs token refresh when needed.
// Also, it now includes the response body in the error message.
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;
    // If skipAuth flag is set, do not attempt token refresh; simply reject the error.
    if (originalRequest.skipAuth) {
      if (error.response && error.response.data) {
        error.message = `${error.message} - ${JSON.stringify(
          error.response.data
        )}`;
      }
      return Promise.reject(error);
    }

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

      // If there is no refresh token, redirect to login.
      if (!refresh_token) {
        const globalLogout = getGlobalLogout();
        if (globalLogout) {
          globalLogout();
        }
        router.replace("/auth");
        return Promise.reject(error);
      }

      const fingerprint = await generateFingerprint();

      return new Promise((resolve, reject) => {
        // Use axios for the refresh token request and set skipAuth to bypass the expired token attachment
        axios
          .post(
            "/auth/refresh-token",
            {},
            {
              baseURL: BASE_URL,
              headers: {
                "application-id": fingerprint,
                Authorization: "Bearer " + refresh_token,
              },
            }
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
            await asyncRemoveData("isLoggedIn");
            // Logout globally
            const globalLogout = getGlobalLogout();
            if (globalLogout) {
              globalLogout();
            }
            // Redirect to the login page
            router.replace("/auth");
            // Append the response body to the error message if available
            if (err.response && err.response.data) {
              err.message = `${err.message} - ${JSON.stringify(
                err.response.data
              )}`;
            }
            reject(err);
          })
          .finally(() => {
            isRefreshing = false;
          });
      });
    }

    if (error.response && error.response.status === 403) {
      const originalRequest = error.config as CustomAxiosRequestConfig;
      // If the request has already been retried once, redirect to clubs index
      if (originalRequest._retry403) {
        router.dismissAll();
        router.replace("/(tabs)/clubs");
        return Promise.reject(error);
      }
      originalRequest._retry403 = true;

      if (isRefreshingPermissions) {
        return new Promise<boolean>((resolve, reject) => {
          failedPermissionQueue.push({ resolve, reject });
        }).then((shouldRetry: boolean) => {
          if (shouldRetry) {
            return axiosInstance(originalRequest);
          } else {
            router.dismissAll();
            router.replace("/(tabs)/clubs");
            return Promise.reject(error);
          }
        });
      }

      isRefreshingPermissions = true;

      return new Promise((resolve, reject) => {
        // Trigger forced permissions refresh
        triggerPermissionRefresh();
        // Wait for the permissions refresh to complete (adjust the timeout if needed)
        setTimeout(() => {
          isRefreshingPermissions = false;
          // Process any queued requests
          failedPermissionQueue.forEach(prom => prom.resolve(true));
          failedPermissionQueue = [];
          // Retry the original request
          axiosInstance(originalRequest)
            .then(resolve)
            .catch(err => {
              // If still failing with 403, redirect to clubs index
              router.dismissAll();
              router.replace("/(tabs)/clubs");
              reject(err);
            });
        }, 1000);
      });
    }

    // For other errors, append the response body to the error message if available
    if (error.response && error.response.data) {
      error.message = `${error.message} - ${JSON.stringify(
        error.response.data
      )}`;
    }
    return Promise.reject(error);
  }
);

export { axiosInstance, BASE_URL };
