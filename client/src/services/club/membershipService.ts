import { axiosInstance } from "../api";

export const getMemberships = async (club_id: string | string[]) => {
  try {
    const response = await axiosInstance.get(`/clubs/${club_id}/memberships`);
    return response.data;
  } catch (error) {
    console.error("Error during getMemberships call:", error);
    throw error;
  }
};

export const createMembership = async (
  club_id: string | string[],
  name: string,
  description: string,
  price: number,
  currency: string,
  duration: number,
  duration_unit: string,
  status: string
) => {
  try {
    const request_body = {
      name,
      description,
      price,
      currency,
      duration,
      duration_unit,
      status,
    };

    const response = await axiosInstance.post(
      `/clubs/${club_id}/memberships`,
      request_body
    );
    return response.data;
  } catch (error) {
    console.error("Error during createMembership call:", error);
    throw error;
  }
};

export const getMembership = async (
  club_id: string | string[],
  membership_id: string | string[]
) => {
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
  club_id: string | string[],
  membership_id: string | string[],
  name: string,
  description: string,
  price: number,
  currency: string,
  duration: number,
  duration_unit: string,
  status: string
) => {
  try {
    const request_body = {
      name,
      description,
      price,
      currency,
      duration,
      duration_unit,
      status,
    };

    const response = await axiosInstance.put(
      `/clubs/${club_id}/memberships/${membership_id}`,
      request_body
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateMembership call:", error);
    throw error;
  }
};

export const deleteMembership = async (
  club_id: string | string[],
  membership_id: string | string[],
  password: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/memberships/${membership_id}`,
      { data: { password } }
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteMembership call:", error);
    throw error;
  }
};

export const buyMembership = async (
  club_id: string | string[],
  membership_id: string | string[]
) => {
  try {
    const response = await axiosInstance.post(
      `/clubs/${club_id}/memberships/${membership_id}/buy`
    );
    return response.data;
  } catch (error) {
    console.error("Error during buyMembership call:", error);
    throw error;
  }
};

export const cancelMembership = async (
  club_id: string | string[],
  membership_id: string | string[]
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/memberships/${membership_id}/cancel`
    );
    return response.data;
  } catch (error) {
    console.error("Error during cancelMembership call:", error);
    throw error;
  }
};

export const createMembershipAccess = async (
  club_id: string | string[],
  membership_id: string | string[],
  program_id: string | string[],
  additional_fee: number
) => {
  try {
    const request_body = [
      {
        program_id,
        additional_fee,
      }
    ];

    const response = await axiosInstance.post(
      `/clubs/${club_id}/memberships/${membership_id}/access`,
      request_body
    );
    return response.data;
  } catch (error) {
    console.error("Error during createMembershipAccess call:", error);
    throw error;
  }
};

export const updateMembershipAccess = async (
  club_id: string | string[],
  membership_id: string | string[],
  program_id: string | string[],
  new_additional_fee: number
) => {
  try {
    const response = await axiosInstance.put(
      `/clubs/${club_id}/memberships/${membership_id}/access?program_id=${program_id}&new_additional_fee=${new_additional_fee}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during updateMembershipAccess call:", error);
    throw error;
  }
};

export const deleteMembershipAccess = async (
  club_id: string | string[],
  membership_id: string | string[],
  program_id: string | string[]
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/memberships/${membership_id}/access`,
      { data: [program_id] }
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteMembershipAccess call:", error);
    throw error;
  }
}

export const getMembershipUsers = async (
  club_id: string | string[],
  membership_id: string | string[]
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/memberships/${membership_id}/users`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getMembershipUsers call:", error);
    throw error;
  }
}