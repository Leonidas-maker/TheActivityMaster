import { axiosInstance } from "../api";

export const getMemberships = async (club_id: string) => {
  try {
    const response = await axiosInstance.get(`/clubs/${club_id}/memberships`);
    return response.data;
  } catch (error) {
    console.error("Error during getMemberships call:", error);
    throw error;
  }
};

export const createMembership = async (club_id: string) => {
  try {
    const response = await axiosInstance.post(`/clubs/${club_id}/memberships`);
    return response.data;
  } catch (error) {
    console.error("Error during createMembership call:", error);
    throw error;
  }
};

export const getMembership = async (club_id: string, membership_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/memberships/${membership_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getMembership call:", error);
    throw error;
  }
};

export const updateMembership = async (
  club_id: string,
  membership_id: string
) => {
  try {
    const response = await axiosInstance.put(
      `/clubs/${club_id}/memberships/${membership_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateMembership call:", error);
    throw error;
  }
};

export const deleteMembership = async (
  club_id: string,
  membership_id: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/memberships/${membership_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteMembership call:", error);
    throw error;
  }
};
