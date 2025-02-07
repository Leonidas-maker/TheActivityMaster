import { axiosInstance } from "./static";

export const getGerTerms = async (): Promise<any> => {
  try {
    const response = await axiosInstance.get("/t&c/ger.md");
    return response.data;
  } catch (error) {
    console.error("Error during getGerTerms call:", error);
    throw error;
  }
};

export const getEnTerms = async (): Promise<any> => {
  try {
    const response = await axiosInstance.get("/t&c/en.md");
    return response.data;
  } catch (error) {
    console.error("Error during getEnTerms call:", error);
    throw error;
  }
};
