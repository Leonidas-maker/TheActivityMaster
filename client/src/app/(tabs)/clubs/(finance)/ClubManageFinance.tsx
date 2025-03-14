import React, { useEffect, useState } from "react";
import { View, ScrollView } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { getBookings } from "@/src/services/club/bookingService";
import { useLocalSearchParams } from "expo-router";

interface Booking {
  session_id?: string;
  booking_type: string;
  program_id?: string;
  price: number;
  user: {
    id: string;
    first_name: string;
    last_name: string;
  };
}

const ClubManageFinance = () => {
  const { t } = useTranslation("clubs");
  const { club_id } = useLocalSearchParams();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Call getBookings and use the provided example response
        const bookings: Booking[] = await getBookings(club_id);
        // If bookings are available, take the first one
        if (bookings && bookings.length > 0) {
          setBooking(bookings[0]);
        }
      } catch (error) {
        console.error("Error fetching booking data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary justify-center">
        <DefaultText text={t("loading")} />
      </View>
    );
  }

  if (!booking) {
    return (
      <View className="h-screen bg-light_primary dark:bg-dark_primary py-4">
        <Heading text={t("noBookings")} />
      </View>
    );
  }

  return (
    <ScrollView className="flex h-screen bg-light_primary dark:bg-dark_primary p-4">
      <View className="m-2 p-2 bg-light_secondary dark:bg-dark_secondary rounded-xl shadow-[rgba(0,0,0,0.5)_0px_5px_4px_0px]">
        {booking.session_id && (
          <DefaultText text={`${t("sessionId")} ${booking.session_id}`} />
        )}
        <DefaultText text={`${t("bookingType")} ${booking.booking_type}`} />
        {booking.program_id && (
          <DefaultText text={`${t("programId")} ${booking.program_id}`} />
        )}
        <DefaultText text={`${t("price_booked")} ${booking.price}`} />
        <DefaultText text={`${t("userName")} ${booking.user.first_name} ${booking.user.last_name}`} />
      </View>
    </ScrollView>
  );
};

export default ClubManageFinance;