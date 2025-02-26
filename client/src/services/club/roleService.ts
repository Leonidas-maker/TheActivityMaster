import { axiosInstance } from "../api";

interface ClubRole {
  level: number;
  name: string;
  description: string;
  permissions: string[];
}

export const createClubRole = async (club_id: string, role: ClubRole) => {
  try {
    const requestBody = {
      role,
    };

    const response = await axiosInstance.post(
      `/clubs/${club_id}/roles`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during createClubRole call:", error);
    throw error;
  }
};

export const getClubRoles = async (club_id: string) => {
  try {
    const response = await axiosInstance.get(`/clubs/${club_id}/roles/all`);
    return response.data;
  } catch (error) {
    console.error("Error during getClubRoles call:", error);
    throw error;
  }
};

export const getClubRole = async (club_id: string, role_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/roles/${role_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getClubRole call:", error);
    throw error;
  }
};

export const updateClubRole = async (
  club_id: string,
  role_id: string,
  role: ClubRole
) => {
  try {
    const requestBody = {
      role,
    };

    const response = await axiosInstance.put(
      `/clubs/${club_id}/roles/${role_id}`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateClubRole call:", error);
    throw error;
  }
};

export const deleteClubRole = async (club_id: string, role_id: string) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/roles/${role_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteClubRole call:", error);
    throw error;
  }
};

export const getClubRoleMembers = async (club_id: string, role_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/roles/${role_id}/members`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getClubRoleMembers call:", error);
    throw error;
  }
};

export const getClubPermissions = async () => {
  try {
    const response = await axiosInstance.get(`/clubs/permissions`);
    return response.data;
  } catch (error) {
    console.error("Error during getClubPermissions call:", error);
    throw error;
  }
};
