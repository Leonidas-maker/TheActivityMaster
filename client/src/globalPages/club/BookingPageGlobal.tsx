import React, { useState } from "react";
import { ScrollView, View, TouchableOpacity, useColorScheme, Text, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import Toast from "react-native-toast-message";
import Heading from "@/src/components/textFields/Heading";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { createBooking } from "@/src/services/club/bookingService";
import { buyMembership } from "@/src/services/club/membershipService";
import { useTranslation } from "react-i18next";
import Subheading from "@/src/components/textFields/Subheading";
import { useAuth } from '@/src/provider/AuthContextProvider';

interface BookingPageGlobalProps {
    club_id: string | string[];
    route_name: string | string[];
    program_id?: string | string[];
    session_id?: string | string[];
    is_membership?: boolean;
    membership_id?: string | string[];
    price?: number;
    name?: string;
}

const BookingPageGlobal = ({
    club_id,
    route_name,
    program_id = "",
    session_id = "",
    is_membership = false,
    membership_id = "",
    price = 0,
    name = "",
}: BookingPageGlobalProps) => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const colorScheme = useColorScheme();
    const [bookingLoading, setBookingLoading] = useState(false);
    const { authState } = useAuth();
    const { isLoggedIn } = authState;

    const handleBooking = async () => {
        setBookingLoading(true);
        try {
            if (is_membership) {
                // Call buyMembership if it's a membership booking
                await buyMembership(club_id, membership_id);
            } else {
                // Prepare arrays for program_ids and session_ids
                let program_ids: string[] = [];
                let session_ids: string[] = [];

                if (program_id && typeof program_id === "string" && program_id !== "") {
                    program_ids = [program_id];
                } else if (Array.isArray(program_id)) {
                    program_ids = program_id;
                }

                if (session_id && typeof session_id === "string" && session_id !== "") {
                    session_ids = [session_id];
                } else if (Array.isArray(session_id)) {
                    session_ids = session_id;
                }

                // Call createBooking with both program_ids and session_ids
                await createBooking(club_id, program_ids, session_ids);
            }
            // Navigate to bookingInfo page on successful booking
            router.dismissAll();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        } finally {
            setBookingLoading(false);
        }
    };

    const buttonBg = colorScheme === "dark" ? "bg-white" : "bg-black";
    const buttonTextColor = colorScheme === "dark" ? "text-black" : "text-white";

    return (
        <ScrollView className="bg-light_primary dark:bg-dark_primary flex-1">
            <View className="p-4">
                <Heading text={t("bookingTitle")} />
                <View className="mt-4">
                    <Heading text={name} />
                    <Subheading text={t("price", { value: (price && price / 100).toFixed(2) })} />
                </View>
                <TouchableOpacity
                    onPress={handleBooking}
                    disabled={bookingLoading}
                    className={`mx-4 my-4 p-4 rounded-xl items-center justify-center ${buttonBg}`}
                >
                    {bookingLoading ? (
                        <ActivityIndicator size="small" color={colorScheme === "dark" ? "#000" : "#fff"} />
                    ) : (
                        <Text className={buttonTextColor}>{t("buy")}</Text>
                    )}
                </TouchableOpacity>
            </View>
            <DefaultToast />
        </ScrollView>
    );
};

export default BookingPageGlobal;