import { axiosInstance } from "../api";

export const verifyMail = async (
  user_id: string,
  expires: string,
  signature: string
) => {
  try {
    const response = await axiosInstance.post(
      `/verification/verify_email?user_id=${user_id}&expires=${expires}&signature=${signature}`
    );

    return response.data;
  } catch (error) {
    console.error("Verify mail error:", error);
    throw error;
  }
};
