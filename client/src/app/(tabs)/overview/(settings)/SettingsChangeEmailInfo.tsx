import React from "react";
import { View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import Heading from "@/src/components/textFields/Heading";
import Subheading from "@/src/components/textFields/Subheading";

const SettingsChangeEmailInfo = () => {
    const router = useRouter();
    const { t } = useTranslation("settings");

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <View className="p-4">
                <Heading text={t("change_email_info_title")} />
            </View>
            <Subheading text={t("change_email_info_subheading")} />
            <DefaultButton text={t("change_email_go_back")} onPress={() => router.dismissTo("/(tabs)/overview")} />
        </View>
    );
};

export default SettingsChangeEmailInfo;