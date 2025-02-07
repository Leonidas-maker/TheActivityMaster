// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import axios, { AxiosInstance, AxiosError, AxiosResponse } from "axios";
import generateFingerprint from "../fingerprint/Fingerprint"; // Adjust the path accordingly

// Define the base URL
// const BASE_URL = "https://theactivitymaster.de/api/v1";
const BASE_URL = "http://localhost:8001/api/v1";
axios.defaults.baseURL = BASE_URL;

// Create an axios instance
const axiosInstance: AxiosInstance = axios.create();

// Add a request interceptor to include the fingerprint (application-id) in the headers for every request
axiosInstance.interceptors.request.use(
  async (config) => {
    try {
      // Generate a new fingerprint for every request
      const fingerprint = await generateFingerprint();
      // Attach the fingerprint as the "application-id" header
      if (fingerprint) {
        config.headers = {
          ...config.headers,
          "application-id": fingerprint,
        } as any;
      }
    } catch (error) {
      console.error("Error generating fingerprint:", error);
    }
    return config;
  },
  (error) => {
    // Handle any errors that occur during the request setup
    return Promise.reject(error);
  }
);

//TODO: Add a response interceptor
// Response interceptor: check for error responses and handle 401 errors
// axiosInstance.interceptors.response.use(
//     (response: AxiosResponse) => response,
//     (error: AxiosError) => {
//       if (error.response && error.response.status === 401) {
//         //TODO Refresh the token and retry the request here
//         console.error("Unauthorized request. Refresh the token and retry the request.");
//         return error.response.status;
//       }
//       // Optionally handle other status codes or errors here
//       return Promise.reject(error);
//     }
//   );

export { axiosInstance, BASE_URL };
