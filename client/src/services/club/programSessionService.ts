import { axiosInstance } from "../api";

//TODO: Export interfaces in a separate file and import them here
interface sessions {
  session_type: "course" | "event";
  capacity: number;
  price: number;
  start_datetime: string;
  end_datetime: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  start_date: string;
  end_date: string;
  address: address;
}

interface address {
  street: string;
  postal_code: string;
  city: string;
  state: string;
  country: string;
}

export const getSession = async (club_id: string, program_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/programs/${program_id}/sessions`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getSessions call:", error);
    throw error;
  }
};

export const createSession = async (
  club_id: string,
  program_id: string,
  session: sessions
) => {
  try {
    const requestBody = {
      session,
    };

    const response = await axiosInstance.post(
      `/clubs/${club_id}/programs/${program_id}/sessions`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during createSession call:", error);
    throw error;
  }
};

export const updateSession = async (
  club_id: string,
  program_id: string,
  session_id: string,
  session: sessions,
  null_end_date: boolean,
  refresh_future_occurrences: boolean
) => {
  try {
    const requestBody = {
      session,
      null_end_date,
      refresh_future_occurrences,
    };

    const response = await axiosInstance.put(
      `/clubs/${club_id}/programs/${program_id}/sessions/${session_id}`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateSession call:", error);
    throw error;
  }
};

export const deleteSession = async (
  club_id: string,
  program_id: string,
  session_id: string,
  message: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/programs/${program_id}/sessions/${session_id}`,
      { data: message }
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteSession call:", error);
    throw error;
  }
};

export const getSessions = async (
  club_id: string,
  page: number,
  page_size: number
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/sessions?page=${page}&page_size=${page_size}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getSessions call:", error);
    throw error;
  }
};
