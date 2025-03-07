import { axiosInstance } from "../api";

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

export const getPrograms = async (
  club_id: string | string[],
  page: number,
  page_size: number
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/programs?page=${page}&page_size=${page_size}`
    );

    return response.data;
  } catch (error) {
    console.error("Error during getPrograms call:", error);
    throw error;
  }
};

export const createProgram = async (
  club_id: string | string[],
  name: string,
  description: string,
  price: number | null,
  currency: string,
  pricing_model: "package" | "per_session" | string,
  capacity: number | null,
  membership_required: boolean,
  categories: number[],
  status: "active" | "inactive" | "draft",
  sessions?: sessions[],
) => {
  try {
    const requestBody = {
      name,
      description,
      price,
      currency,
      pricing_model,
      capacity,
      membership_required,
      sessions: sessions ?? [],
      categories,
      status,
    };

    const response = await axiosInstance.post(
      `/clubs/${club_id}/programs`,
      requestBody
    );

    return response.data;
  } catch (error) {
    console.error("Error during createProgram call:", error);
    throw error;
  }
};

export const getProgram = async (club_id: string | string[], program_id: string | string[]) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/programs/${program_id}`
    );

    return response.data;
  } catch (error) {
    console.error("Error during getProgram call:", error);
    throw error;
  }
};

export const updateProgram = async (
  club_id: string | string[],
  program_id: string | string[],
  name: string,
  description: string,
  price: number | null,
  currency: string,
  pricing_model: string,
  capacity: number | null,
  membership_required: boolean,
  categories: number[],
  status?: string,
) => {
  try {
    const requestBody = {
      name,
      description,
      price,
      currency,
      pricing_model,
      capacity,
      membership_required,
      categories,
      ...(status ? { status } : {}),
    };

    const response = await axiosInstance.put(
      `/clubs/${club_id}/programs/${program_id}`,
      requestBody
    );

    return response.data;
  } catch (error) {
    console.error("Error during updateProgram call:", error);
    throw error;
  }
};

export const deleteProgram = async (club_id: string | string[], program_id: string | string[], force: boolean = false) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/programs/${program_id}?force=${force}`
    );

    return response.data;
  } catch (error) {
    console.error("Error during deleteProgram call:", error);
    throw error;
  }
};

export const searchPrograms = async (
    query: string,
    category_id: number,
    min_price: number,
    max_price: number,
    session_type: "course" | "event",
    page: number,
    page_size: number,
) => {
    try {
        const response = await axiosInstance.get(
            `/clubs/programs/search?query=${query}&category_id=${category_id}&min_price=${min_price}&max_price=${max_price}&session_type=${session_type}&page=${page}&page_size=${page_size}`
        );
        return response.data;
    } catch (error) {
        console.error("Error during searchPrograms call:", error);
        throw error;
    }
};

export const getProgramCategories = async (
    language: string
) => {
    try {
        const config = {
            headers: {
                "Accept-Language": language,
            },
        }

        const response = await axiosInstance.get(
            `/clubs/program-categories`,
            config
        );

        return response.data;
    } catch (error) {
        console.error("Error during getProgramCategories call:", error);
        throw error;
    }
};