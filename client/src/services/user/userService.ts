import { axiosInstance } from "../api";
import { secureLoadData } from "../secureStorageService";

export const getUserData = async (): Promise<any> => {
  try {
    const response = await axiosInstance.get("/user/me");

    return response.data;
  } catch (error) {
    console.error("Error during getUserData call:", error);
    throw error;
  }
};

export const register = async (
    username: string,
    email: string,
    first_name: string,
    last_name: string,
    street: string,
    postal_code: string,
    city: string,
    state: string,
    country: string,
    password: string
  ): Promise<any> => {
    try {
      // Prepare the request body with the correct structure
      const requestBody = {
        username,
        email,
        first_name,
        last_name,
        address: {
          street,
          postal_code,
          city,
          state,
          country,
        },
        password,
      };
  
      // Call the /user/register endpoint with the provided credentials
      const response = await axiosInstance.post("/user/register", requestBody, { skipAuth: true });
      return response.data;
    } catch (error) {
      console.error("Error during register call:", error);
      throw error;
    }
  };  

export const changePassword = async (
  old_password: string,
  new_password: string
): Promise<any> => {
  try {
    const requestBody = {
      new_password,
      old_password,
    };

    const response = await axiosInstance.post("/user/me/change_password", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during changePassword call:", error);
    throw error;
  }
}
