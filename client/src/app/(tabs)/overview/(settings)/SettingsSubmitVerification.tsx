import React from "react";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { View } from "react-native";

const SettingsSubmitVerification = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    return (
        <View className="flex bg-light_primary dark:bg-dark_primary">
            <Heading text={t("submit_verification")} />

            <DefaultText text={t("submit_verification_text")} />

            <DefaultButton text={t("submit_verification_button")} onPress={() => router.navigate("/")} />
        </View>
    )
}

export default SettingsSubmitVerification;