import { axiosInstance } from "../api";

export const logout = async (): Promise<any> => {
  try {
    const response = await axiosInstance.delete("/auth/logout");
    return response.data;
  } catch (error) {
    console.error("Logout failed:", error);
    throw error;
  }
};

export const logoutAll = async (): Promise<any> => {
  try {
    const response = await axiosInstance.delete("/auth/logout-all");
    return response.data;
  } catch (error) {
    console.error("Logout all failed:", error);
    throw error;
  }
};
