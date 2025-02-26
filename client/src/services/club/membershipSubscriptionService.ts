import { axiosInstance } from "../api";

export const getSubscriptions = async (club_id: string) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/memberships/subscriptions`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getSubscriptions call:", error);
    throw error;
  }
};

export const getSubscription = async (
  club_id: string,
  membership_id: string,
  subscription_id: string
) => {
  try {
    const response = await axiosInstance.get(
      `/clubs/${club_id}/memberships/${membership_id}/subscriptions/${subscription_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during getSubscription call:", error);
    throw error;
  }
};

export const deleteSubscription = async (
  club_id: string,
  membership_id: string,
  subscription_id: string
) => {
  try {
    const response = await axiosInstance.delete(
      `/clubs/${club_id}/memberships/${membership_id}/subscriptions/${subscription_id}`
    );
    return response.data;
  } catch (error) {
    console.error("Error during deleteSubscription call:", error);
    throw error;
  }
};
