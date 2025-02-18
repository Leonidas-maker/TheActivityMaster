import React from "react";
import { View } from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { logoutAll } from "@/src/services/auth/tokenService";
import { secureRemoveData } from "@/src/services/secureStorageService";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { asyncRemoveData } from "@/src/services/asyncStorageService";
import Heading from "@/src/components/textFields/Heading";

const SettingsLogout = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    const handleLogoutAllPress = async () => {
        await logoutAll().then(() => {
            asyncRemoveData("isLoggedIn");
            secureRemoveData("access_token");
            secureRemoveData("refresh_token");
            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/(tabs)");
        });
    };

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <View className="py-4">
                <Heading text={t("logout_message")} />
            </View>
            <DefaultButton text={t("logout_all_btn")} onPress={handleLogoutAllPress} />
        </View>
    );
};

export default SettingsLogout;