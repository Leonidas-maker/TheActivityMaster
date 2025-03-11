import { axiosInstance } from "../api";

export const rescheduleOccurrence = async (
  club_id: string | string[],
  program_id: string | string[],
  session_id: string | string[],
  occurrence_id: string | string[],
  note: string,
  start_datetime: string,
  end_datetime: string
) => {
  try {
    const requestBody = [
      {
        occurrence_id,
        note,
        start_datetime,
        end_datetime,
      }
    ];

    const response = await axiosInstance.put(
      `/clubs/${club_id}/programs/${program_id}/sessions/${session_id}/occurrences/reschedule`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during rescheduleOccurrence call:", error);
    throw error;
  }
};

export const reinstateOccurrence = async (
  club_id: string | string[],
  program_id: string | string[],
  session_id: string | string[],
  occurrence_id: string | string[],
  note: string
) => {
  try {
    const requestBody = [
      {
        occurrence_id,
        note,
      }
    ];

    const response = await axiosInstance.put(
      `/clubs/${club_id}/programs/${program_id}/sessions/${session_id}/occurrences/reinstate`,
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during reinstateOccurrence call:", error);
    throw error;
  }
};

export const cancelOccurrence = async (
  club_id: string | string[],
  program_id: string | string[],
  session_id: string | string[],
  occurrence_id: string | string[],
  note: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/programs/${program_id}/sessions/${session_id}/occurrences/${occurrence_id}`,
      {
        data: JSON.stringify(note),
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error during cancelOccurrence call:", error);
    throw error;
  }
};