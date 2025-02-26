import { axiosInstance } from "../api";

export const getEmployees = async (club_id: string) => {
  try {
    const response = await axiosInstance.get(`/clubs/${club_id}/employees/all`);
    return response.data;
  } catch (error) {
    console.error("Error during getEmployees call:", error);
    throw error;
  }
};

export const getEmployee = async (club_id: string, user_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/employees?user_id=${user_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getEmployee call:", error);
    throw error;
  }
};

export const addEmployee = async (
  club_id: string,
  user_ident: string,
  level: number
) => {
  try {
    const requestBody = {
      user_ident,
      level,
    };

    const response = await axiosInstance.post(
      `/clubs/${club_id}/employees`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during addEmployee call:", error);
    throw error;
  }
};

export const updateEmployee = async (
  club_id: string,
  user_id: string,
  level: number
) => {
  try {
    const requestBody = {
      user_id,
      level,
    };

    const response = await axiosInstance.put(
      `/clubs/${club_id}/employees`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateEmployee call:", error);
    throw error;
  }
};

export const deleteEmployee = async (club_id: string, user_id: string) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/employees?user_id=${user_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteEmployee call:", error);
    throw error;
  }
};
