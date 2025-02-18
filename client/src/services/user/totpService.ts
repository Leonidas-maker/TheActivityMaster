import { axiosInstance } from "../api";

export const totpRegisterInit = async (): Promise<any> => {
  try {
    const response = await axiosInstance.post("/user/me/totp_register_init");
    return response.data;
  } catch (error) {
    console.error("Error during totpRegisterInit call:", error);
    throw error;
  }
};
