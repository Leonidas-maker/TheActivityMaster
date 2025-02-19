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

export const totpRegister = async (_2fa_code: string): Promise<any> => {
  try {
    const response = await axiosInstance.post("/user/me/totp_register?_2fa_code=" + _2fa_code);
    return response.data;
  } catch (error) {
    console.error("Error during totpRegister call:", error);
    throw error;
  }
};
