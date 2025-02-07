import { axiosInstance } from "@/src/services/api";

/**
 * Send a login request to the /auth/login endpoint.
 *
 * @param ident - The identifier (e.g., username or email)
 * @param password - The user's password
 * @returns A promise that resolves with the login response data.
 */
export const login = async (ident: string, password: string): Promise<any> => {
  try {
    // Prepare the request body
    const requestBody = {
      ident,
      password,
    };

    // Call the /auth/login endpoint with the provided credentials
    const response = await axiosInstance.post("/auth/login", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during login call:", error);
    throw error;
  }
};

/**
 * Verify 2FA code using the /auth/verify-code-2fa endpoint.
 *
 * @param securityToken - The security token obtained from the login response.
 * @param code - The 2FA code to verify.
 * @param methods - The authentication methods from the login response.
 * @returns A promise that resolves with the 2FA verification response data.
 */
export const verify2fa = async (
  securityToken: string,
  code: string,
  methods: string[]
): Promise<any> => {
  try {
    // Determine if TOTP is used. If "totp" is present in the methods array, set is_totp to true.
    const isTotp = methods.includes("totp");

    // Prepare the request body.
    const requestBody = {
      code,
      is_totp: isTotp,
    };

    // Configure the headers with the security token.
    const config = {
      headers: {
        Authorization: `Bearer ${securityToken}`,
      },
    };

    // Call the /auth/verify-code-2fa endpoint with the request body and headers.
    const response = await axiosInstance.post(
      "/auth/verify-code-2fa",
      requestBody,
      config
    );

    return response.data;
  } catch (error) {
    console.error("Error during 2FA verification:", error);
    throw error;
  }
};
