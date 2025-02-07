import { axiosInstance } from "../api";
import { secureLoadData } from "../secureStorageService";

export const getUserData = async (): Promise<any> => {
  try {
    //TODO: Add Logic to get access_token with validation and refresh
    const access_token = await secureLoadData("access_token");

    // Configure the headers with the access token.
    const config = {
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    };

    const response = await axiosInstance.get("/user/me", config);

    return response.data;
  } catch (error) {
    console.error("Error during getUserData call:", error);
    throw error;
  }
};
