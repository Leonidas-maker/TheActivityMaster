import React, { useEffect, useState } from "react";
import { View, ScrollView } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { getUserBooked } from "@/src/services/user/userService";
import { getClub } from "@/src/services/club/clubService";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";

interface Booking {
    session_id: string;
    booking_type: string;
    id: string;
    club_id: string;
    program_id: string;
    user_id: string;
    status: string;
    transaction_id: string;
    price: number;
    pricing_model: string;
}

interface Club {
    name: string;
    description: string;
    address: {
        street: string;
        postal_code: string;
        city: string;
        state: string;
        country: string;
    };
    id: string;
    is_deleted: boolean;
    owners: {
        first_name: string;
        last_name: string;
        email: string;
    }[];
}

const BillingBooked = () => {
    const { t } = useTranslation("billing");
    const [booking, setBooking] = useState<Booking | null>(null);
    const [club, setClub] = useState<Club | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const userBookings: Booking[] = await getUserBooked();
                if (userBookings && userBookings.length > 0) {
                    const firstBooking = userBookings[0];
                    setBooking(firstBooking);
                    const clubData: Club = await getClub(firstBooking.club_id);
                    setClub(clubData);
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
                {club && (
                    <DefaultText text={`${t("clubName")} ${club.name}`} />
                )}
                <DefaultText text={`${t("bookingType")} ${booking.booking_type}`} />
                <DefaultText text={`${t("status")} ${booking.status}`} />
                <DefaultText text={`${t("transactionId")} ${booking.transaction_id}`} />
                <DefaultText text={`${t("price")} ${booking.price}`} />
                <DefaultText text={`${t("pricingModel")} ${booking.pricing_model}`} />
            </View>
        </ScrollView>
    );
};

export default BillingBooked;