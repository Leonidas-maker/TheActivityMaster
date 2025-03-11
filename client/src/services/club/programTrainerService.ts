import { axiosInstance } from "../api";

export const getTrainers = async (club_id: string | string[], program_id: string | string[]) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/programs/${program_id}/trainers`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getTrainers call:", error);
    throw error;
  }
};

export const addTrainer = async (
  club_id: string | string[],
  program_id: string | string[],
  user_id: string
) => {
  try {
    const response = await axiosInstance.post(
      `/clubs/${club_id}/programs/${program_id}/trainers?user_id=${user_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during addTrainer call:", error);
    throw error;
  }
};

export const removeTrainer = async (
  club_id: string | string[],
  program_id: string | string[],
  trainer_id: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/programs/${program_id}/trainers/${trainer_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during removeTrainer call:", error);
    throw error;
  }
};
