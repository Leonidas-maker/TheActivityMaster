import React from "react";
import { ScrollView, View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

const SettingsVerificationStatus = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    return (
        <ScrollView className="flex h-screen bg-light_primary dark:bg-dark_primary">
            <Heading text={t("verification_status")} />

            <DefaultText text={t("verification_status_text")} />

            <DefaultButton text={t("submit_verification_button")} onPress={() => router.navigate("/")} />
        </ScrollView>
    )
}

export default SettingsVerificationStatus;