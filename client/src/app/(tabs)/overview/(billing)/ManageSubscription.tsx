import React, { useEffect } from "react";
import { View, useColorScheme, Pressable } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { cancelMembership } from "@/src/services/club/membershipService";
import { Alert } from "react-native";
import Toast from "react-native-toast-message";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Subheading from "@/src/components/textFields/Subheading";

const ManageSubscription = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("billing");
    const { membership, start_datetime, end_datetime } = useLocalSearchParams();

    // Parse the membership data from query params
    const parsedMembership = membership ? JSON.parse(decodeURIComponent(membership as string)) : null;

    // Helper function to format time as HH:MM
    const formatTime = (dateStr: string): string => {
        const date = new Date(dateStr);
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    };

    // Helper function to format date as DD.MM.YYYY
    const formatDate = (dateStr: string): string => {
        const date = new Date(dateStr);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    };

    const handleCancelMembership = () => {
        Alert.alert(
            t("cancelConfirmTitle"),
            t("cancelConfirmMessage"),
            [
                {
                    text: t("cancelNo"),
                    style: "cancel"
                },
                {
                    text: t("cancelYes"),
                    onPress: async () => {
                        try {
                            await cancelMembership(parsedMembership.membership.club_id, parsedMembership.membership.id);
                            Toast.show({
                                type: "success",
                                text1: t("cancelSuccess")
                            });
                            router.dismissAll();
                        } catch (error) {
                            Toast.show({
                                type: "error",
                                text1: t("cancelError"),
                                text2: t("cancelErrorMessage")
                            });
                        }
                    }
                }
            ]
        );
    };

    const colorScheme = useColorScheme();
    const isLight = colorScheme === "light";
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);
 
    return (
        <View className="flex h-screen bg-light_primary dark:bg-dark_primary p-4">
            <Heading text={t("title")} />
            {parsedMembership && (
                <>
                    <View className="m-4 justify-center items-center">
                        <DefaultText text={`${t("membershipName")}: ${parsedMembership.membership.name}`} />
                        <DefaultText text={`${t("price")}: ${(parsedMembership.membership.price / 100).toFixed(2)} ${parsedMembership.membership.currency}`} />
                        <DefaultText text={`${t("duration")}: ${parsedMembership.membership.duration} ${parsedMembership.membership.duration_unit}`} />
                        <DefaultText text={`${t("startDateTime")}: ${formatDate(start_datetime as string)} ${formatTime(start_datetime as string)}`} />
                        <DefaultText text={`${t("endDateTime")}: ${formatDate(end_datetime as string)} ${formatTime(end_datetime as string)}`} />
                        <View className="py-2" />
                        {parsedMembership.status === "Active" ? (
                            <DefaultButton text={t("cancelButton")} onPress={handleCancelMembership} />
                        ) : (
                            <Subheading text={t("membershipInactive")} />
                        )}
                    </View>
                </>
            )}
        </View>
    );
};

export default ManageSubscription;