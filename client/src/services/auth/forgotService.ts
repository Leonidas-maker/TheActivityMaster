import { axiosInstance } from "../api";

export const forgotPassword = async (ident: string) => {
  try {
    const response = await axiosInstance.post(
      `/auth/forgot-password?ident=${ident}`
    );

    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};

export const resetPassword = async (
  password: string,
  security_token: string
) => {
  try {
    const config = {
      headers: {
        Authorization: `Bearer ${security_token}`,
      },
      skipAuth: true,
    };

    const requestBody = {
      password,
    };

    const response = await axiosInstance.post(
      `/auth/reset-password`,
      requestBody,
      config
    );
    
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
