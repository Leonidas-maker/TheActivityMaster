import { axiosInstance } from "../api";

//TODO: Export interfaces in a separate file and import them here
interface sessions {
  session_type: string;
  capacity: number | null;
  price: number | null;
  start_datetime: string | null;
  end_datetime: string | null;
  day_of_week: string | null;
  start_time: string | null;
  end_time: string | null;
  start_date: string | null;
  end_date: string | null;
  address: address | null;
}

interface address {
  street: string;
  postal_code: string;
  city: string;
  state: string;
  country: string;
}

export const getSessions = async (
  club_id: string | string[],
  program_id: string | string[]
) => {
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
  club_id: string | string[],
  program_id: string | string[],
  session: sessions
) => {
  try {
    // Send the session data directly instead of wrapping it in a "session" property.
    const response = await axiosInstance.post(
      `/clubs/${club_id}/programs/${program_id}/sessions`,
      session
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

export const getClubSessions = async (
  club_id: string | string[],
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
