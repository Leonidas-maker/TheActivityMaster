import React from "react";
import { View } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

const VerifyMailConfirm = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <Heading text={t("verify_email_heading")} />
            <DefaultText text={t("verify_email_description")} />
            <DefaultButton text={t("verify_email_button")} onPress={() => router.navigate("/(tabs)")} />
            <DefaultToast />
        </View>
    );
}

export default VerifyMailConfirm;