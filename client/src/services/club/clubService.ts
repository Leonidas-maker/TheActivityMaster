import { axiosInstance } from "../api";

interface address {
  street: string;
  postal_code: string;
  city: string;
  state: string;
  country: string;
}

export const createClub = async (
  name: string,
  description: string,
  address: address
) => {
  try {
    const requestBody = {
      name,
      description,
      address,
    };

    const response = await axiosInstance.post("/clubs", requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during createClub call:", error);
    throw error;
  }
};

export const getClub = async (club_id: string | string[]) => {
  try {
    const response = await axiosInstance.get(`/clubs/${club_id}`);
    return response.data;
  } catch (error) {
    console.error("Error during getClub call:", error);
    throw error;
  }
};

export const getClubs = async (
  page: number,
  page_size: number,
  city: string
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs?page=${page}&page_size=${page_size}&city=${city}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getClubs call:", error);
    throw error;
  }
};

export const searchClubs = async (
  query: string,
  page: number,
  page_size: number
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/search?query=${query}&page=${page}&page_size=${page_size}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during searchClubs call:", error);
    throw error;
  }
};

export const updateClubName = async (
  club_id: string | string[],
  name: string,
  description: string,
) => {
  try {
    const requestBody = {
      name,
      description,
    };

    const response = await axiosInstance.put(`/clubs/${club_id}`, requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during updateClubName call:", error);
    throw error;
  }
};

export const updateClubAddress = async (
  club_id: string | string[],
  address: address,
) => {
  try {
    const requestBody = {
      address,
    };

    const response = await axiosInstance.put(`/clubs/${club_id}`, requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during updateClubAddress call:", error);
    throw error;
  }
};

export const deleteClub = async (club_id: string | string[]) => {
  try {
    const response = await axiosInstance.delete(`/clubs/${club_id}`);
    return response.data;
  } catch (error) {
    console.error("Error during deleteClub call:", error);
    throw error;
  }
};
