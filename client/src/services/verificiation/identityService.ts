import { axiosInstance } from "../api";

interface IdentityVerificationData {
  image_files: File[];  
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
  image_files,
  id_card_mrz,
  first_name,
  last_name,
  date_of_birth,
}: IdentityVerificationData) => {
  try {
    const formData = new FormData();

    // Append each image file to the form data
    image_files.forEach((file) => {
      formData.append("image_files", file);
    });

    // Append the rest of the required fields
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
