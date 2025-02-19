import React, { useEffect, useState } from "react";
import { View } from "react-native";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { getUserData } from "@/src/services/user/userService";

const SettingsSecurity = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();
    const [mfaMethods, setMfaMethods] = useState<string[]>([]);

    useEffect(() => {
        // Fetch user data and set the available 2FA methods
        const getUserMethods = async () => {
            const userData = await getUserData();
            setMfaMethods(userData.methods_2fa);
        };
        getUserMethods();
    }, []);

    // Check if the 2FA methods include "email" or "totp"
    const hasEmail = mfaMethods.includes("email");
    const hasTotp = mfaMethods.includes("totp");

    const moduleTitle = t("securityPageNavigator_title");

    const handleMultiFactorPress = () => {
        if (hasEmail) {
            router.navigate("/(tabs)/overview/(settings)/SettingsActivateMFA");
        };
        if (hasTotp) {
            router.navigate("/(tabs)/overview/(settings)/SettingsDeactivateMFA");
        };
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