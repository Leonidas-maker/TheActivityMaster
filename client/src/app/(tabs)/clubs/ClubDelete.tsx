import React from "react";
import { ScrollView, View, Alert } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { deleteClub } from "@/src/services/club/clubService";

const ClubDelete = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();

    const handleDeleteClub = async () => {
        Alert.alert(t("delete_club_alert_title"), t("delete_club_alert_text"), [
            {
                text: t("cancel_btn"),
                style: "cancel",
            },
            {
                text: t("confirm_btn"),
                onPress: () => deleteClubHandler(),
            },
        ]);
    };

    const deleteClubHandler = async () => {
        try {
            await deleteClub(club_id);
            while (router.canGoBack()) {
                router.back();
            }
        } catch (error) {
            console.error("Failed to delete club:", error);
        }
    };

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="items-center">
                <View className="py-4">
                    <Heading text={t("delete_club_heading")} />
                </View>
                <View className="px-4 pb-4">
                    <DefaultText text={t("delete_club_text")} />
                </View>
                <DefaultButton text={t("confirm_club_deletion_btn")} onPress={handleDeleteClub} />
            </View>
        </ScrollView>
    );
}

export default ClubDelete;