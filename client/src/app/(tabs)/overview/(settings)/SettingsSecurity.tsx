import React from "react";
import { View } from "react-native";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

const SettingsSecurity = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    const moduleTitle = t("securityPageNavigator_title");

    const handleMultiFactorPress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsMultiFactor");
    };

    const handleAllLogoutPress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsLogout");
    };

    const handlePasswordChangePress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsChangePassword");
    };

    const securityTexts = [t("settings_changePassword_btn"), t("settings_multiFactor_btn"), t("settings_logout_btn")];

    const securityIcon = ["password", "lock", "logout"];

    const pressFuntions = [handlePasswordChangePress, handleMultiFactorPress, handleAllLogoutPress];

    return (
        <View className="flex h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={moduleTitle}
                texts={securityTexts}
                iconNames={securityIcon}
                onPressFunctions={pressFuntions}
            />
        </View>
    );
};

export default SettingsSecurity;