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
  session_data: Record<string, [number | null, number | null]> | null,
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
      session_data,
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
  search_query: string,
  page: number,
  page_size: number,
  category_id: number | null = null,
  min_price: number | null = null,
  max_price: number | null = null,
  session_type: string | null = null,
) => {
  try {
    const params = new URLSearchParams();

    params.append("search_query", search_query);
    params.append("page", page.toString());
    params.append("page_size", page_size.toString());

    if (category_id !== null) {
      params.append("category_id", category_id.toString());
    }
    if (min_price !== null) {
      params.append("min_price", min_price.toString());
    }
    if (max_price !== null) {
      params.append("max_price", max_price.toString());
    }
    if (session_type !== null) {
      params.append("session_type", session_type);
    }

    const response = await axiosInstance.get(
      `/clubs/programs/search?${params.toString()}`
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