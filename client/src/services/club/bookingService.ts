import { axiosInstance } from "../api";

export const createBooking = async (
  club_id: string | string[],
  program_ids?: string[],
  session_ids?: string[]
) => {
  try {
    const requestBody = [
      {
        club_id,
        program_ids: program_ids || [],
        session_ids: session_ids || [],
      },
    ];

    const response = await axiosInstance.post(`/clubs/book`, requestBody);
    return response.data;
  } catch (error) {
    console.error("Error during createBooking call:", error);
    throw error;
  }
};

export const getBooking = async (booking_id: string) => {
  try {
    const response = await axiosInstance.get(`/clubs/bookings/${booking_id}`);
    return response.data;
  } catch (error) {
    console.error("Error during getBooking call:", error);
    throw error;
  }
};

export const deleteBooking = async (booking_id: string[]) => {
  try {
    const response = await axiosInstance.delete(`/clubs/bookings`, {
      data: booking_id,
    });
    return response.data;
  } catch (error) {
    console.error("Error during deleteBooking call:", error);
    throw error;
  }
};

export const getBookings = async (
  club_id: string,
  program_id?: string,
  session_id?: string
) => {
  try {
    const queryParams = new URLSearchParams();
    if (program_id) queryParams.append("program_id", program_id);
    if (session_id) queryParams.append("session_id", session_id);

    const response = await axiosInstance.get(
      `/clubs/${club_id}/bookings?${queryParams.toString()}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getBookings call:", error);
    throw error;
  }
};
