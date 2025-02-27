import React, { useEffect, useState, useCallback } from "react";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { ScrollView, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useFocusEffect } from "expo-router";
import { getUserClubs } from "@/src/services/user/userService";

const ClubOverview = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    useFocusEffect(
        useCallback(() => {
            getUserClubs()
                .then((clubs) => {
                    console.log(clubs);
                })
                .catch((error) => {
                    console.error("Error during getUserClubs call:", error);
                });
        }, [])
    );

    // ====================================================== //
    // ================= CreateClubNavigator ================ //
    // ====================================================== //
    const handleCreateClub = () => {
        router.push("/(tabs)/overview/(clubs)/ClubCreate");
    };

    const createClubTitle = t("createClub_navigator_title");

    const onPressCreateClubFunctions = [handleCreateClub];

    const createClubTexts = [t("createClub_btn")];

    const createClubIcons = ["add"];

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={createClubTitle}
                texts={createClubTexts}
                iconNames={createClubIcons}
                onPressFunctions={onPressCreateClubFunctions}
            />
        </ScrollView>
    );
};

export default ClubOverview;