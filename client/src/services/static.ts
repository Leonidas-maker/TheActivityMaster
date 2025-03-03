// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import axios, { AxiosInstance } from "axios";

// Define the base URL
// const BASE_URL = "https://theactivitymaster.de/static";
//! For Android testing replace localhost with your local IP address
const BASE_URL = "http://localhost:8001/static";
axios.defaults.baseURL = BASE_URL;

// Create an axios instance
const axiosInstance: AxiosInstance = axios.create();

export { axiosInstance, BASE_URL };
