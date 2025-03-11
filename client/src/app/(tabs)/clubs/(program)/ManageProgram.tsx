import React, { useState, useEffect } from "react";
import { ScrollView, View, TouchableWithoutFeedback, Keyboard, Platform, KeyboardAvoidingView } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ManageProgram = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id, program_id, pricing_model } = useLocalSearchParams();

    const handleUpdateProgramPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/UpdateProgram?club_id=${club_id}&program_id=${program_id}`);
    };

    const handleSessionsPress = () => {
        router.navigate(`/(tabs)/clubs/(session)/ClubManageSessions?club_id=${club_id}&program_id=${program_id}&pricing_model=${pricing_model}`);
    };

    const handleTrainersPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/ManageTrainer?club_id=${club_id}&program_id=${program_id}`);
    };

    const onPressFunctions = [handleSessionsPress, handleTrainersPress, handleUpdateProgramPress];

    const navigatorTitles = [
        t("programs_manage_sessions"), 
        t("programs_manage_trainers"),
        t("programs_manage_update_program"),        
    ];

    const navigatorIcons = ["event", "supervisor-account", "edit"];

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                        <PageNavigator
                            title={t("programs_manage_navigator_title")}
                            onPressFunctions={onPressFunctions}
                            texts={navigatorTitles}
                            iconNames={navigatorIcons}
                        />
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageProgram;
