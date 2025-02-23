import { axiosInstance } from "../static";

export const getCountries = async (): Promise<any> => {
  try {
    const response = await axiosInstance.get("/addresses.json");
    return response.data;
  } catch (error) {
    console.error("Error during getCountries call:", error);
    throw error;
  }
};