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
    const response = await axiosInstance.post("/user/register", requestBody, {
      skipAuth: true,
    });
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

    const response = await axiosInstance.post(
      "/user/me/change_password",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during changePassword call:", error);
    throw error;
  }
};

export const changeUsername = async (
  new_username: string,
  password: string
): Promise<any> => {
  try {
    const requestBody = {
      new_username,
      password,
    };

    const response = await axiosInstance.put("/user/me/username", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during changeUsername call:", error);
    throw error;
  }
};

export const changeEmail = async (
  new_email: string,
  password: string
): Promise<any> => {
  try {
    const requestBody = {
      new_email,
      password,
    };

    const response = await axiosInstance.put("/user/me/email", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during changeEmail call:", error);
    throw error;
  }
};

export const changeAddress = async (
  street: string,
  postal_code: string,
  city: string,
  state: string,
  country: string
): Promise<any> => {
  try {
    const requestBody = {
      address: {
        street,
        postal_code,
        city,
        state,
        country,
      },
    };

    const response = await axiosInstance.put("user/me", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during changeAddress call:", error);
    throw error;
  }
};

export const changeName = async (
  first_name: string,
  last_name: string
): Promise<any> => {
  try {
    const requestBody = {
      first_name,
      last_name,
    };

    const response = await axiosInstance.put("/user/me", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during changeName call:", error);
    throw error;
  }
};

export const deleteUser = async (password: string): Promise<any> => {
  try {
    const requestBody = {
      password,
    };

    const response = await axiosInstance.patch("/user/me", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during deleteUser call:", error);
    throw error;
  }
};
