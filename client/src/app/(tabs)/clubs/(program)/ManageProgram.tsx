import React, { useState, useEffect } from "react";
import {
    ScrollView,
    TouchableWithoutFeedback,
    Keyboard,
    Platform,
    KeyboardAvoidingView
} from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

const ManageProgram = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id, program_id, pricing_model } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    const handleUpdateProgramPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/UpdateProgram?club_id=${club_id}&program_id=${program_id}`);
    };

    const handleSessionsPress = () => {
        router.navigate(`/(tabs)/clubs/(session)/ClubManageSessions?club_id=${club_id}&program_id=${program_id}&pricing_model=${pricing_model}`);
    };

    const handleTrainersPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/ManageTrainer?club_id=${club_id}&program_id=${program_id}`);
    };

    // Build navigation items based on permission check
    const onPressFunctions = [handleSessionsPress];
    const navigatorTitles = [t("programs_manage_sessions")];
    const navigatorIcons = ["event"];

    if (hasPermission("club_update_programs")) {
        onPressFunctions.push(handleTrainersPress, handleUpdateProgramPress);
        navigatorTitles.push(t("programs_manage_trainers"), t("programs_manage_update_program"));
        navigatorIcons.push("supervisor-account", "edit");
    }

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
