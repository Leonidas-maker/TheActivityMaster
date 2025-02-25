import { axiosInstance } from "../api";

interface IdentityVerificationData {
  front_image: string;
  rear_image: string;
  selfie_image: string;
  id_card_mrz: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
}

export const getSelfStatus = async () => {
  try {
    const response = await axiosInstance.get("/verification/identity/self");
    return response.data;
  } catch (error) {
    console.error("Error during getSelfStatus call:", error);
    throw error;
  }
};

export const submitIdentityVerification = async ({
  front_image,
  rear_image,
  selfie_image,
  id_card_mrz,
  first_name,
  last_name,
  date_of_birth,
}: IdentityVerificationData) => {
  try {
    const formData = new FormData();

    formData.append("image_files", {
      uri: front_image,
      name: "front.png",
      type: "image/png",
    } as any);

    formData.append("image_files", {
      uri: rear_image,
      name: "rear.png",
      type: "image/png",
    } as any);

    formData.append("image_files", {
      uri: selfie_image,
      name: "selfie.png",
      type: "image/png",
    } as any);

    // Now append the rest of the fields
    formData.append("id_card_mrz", id_card_mrz);
    formData.append("first_name", first_name);
    formData.append("last_name", last_name);
    formData.append("date_of_birth", date_of_birth);

    // Make the POST request with the form data
    const response = await axiosInstance.post(
      "/verification/identity/submit_identity_verification",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error("Error during submitIdentityVerification call:", error);
    throw error;
  }
};

export const deleteSelfVerification = async () => {
  try {
    const response = await axiosInstance.delete("/verification/identity/self");
    return response.data;
  } catch (error) {
    console.error("Error during deleteSelfVerification call:", error);
    throw error;
  }
};

export const getPendingVerification = async () => {
  try {
    const response = await axiosInstance.get("/verification/identity/pending");
    return response.data;
  } catch (error) {
    console.error("Error during getPendingVerification call:", error);
    throw error;
  }
};

export const getVerification = async (verification_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/verification/identity/get/${verification_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getVerification call:", error);
    throw error;
  }
};

export const getVerificationImage = async (
  verification_id: string,
  index: number
) => {
  try {
    const response = await axiosInstance.get(
      `/verification/identity/get/${verification_id}/image?index=${index}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getVerificationImage call:", error);
    throw error;
  }
};

export const approveVerification = async (verification_id: string) => {
  try {
    const response = await axiosInstance.post(
      `/verification/identity/approve?verification_id=${verification_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during approveVerification call:", error);
    throw error;
  }
};

export const rejectVerification = async (
  identity_verification_id: string,
  reason: string
) => {
  try {
    const requestBody = {
      identity_verification_id,
      reason,
    };

    const response = await axiosInstance.post(
      "/verification/identity/reject",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during rejectVerification call:", error);
    throw error;
  }
};
