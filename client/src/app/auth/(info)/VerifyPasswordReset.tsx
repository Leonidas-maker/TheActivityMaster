import React from "react";
import { View } from "react-native";
import { useTranslation } from "react-i18next";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { useRouter } from "expo-router";
import Heading from "@/src/components/textFields/Heading";
import Subheading from "@/src/components/textFields/Subheading";

const VerifyPasswordReset = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    const handleLoginPress = () => {
        while (router.canGoBack()) {
            router.back();
        }
        router.navigate("/auth");
    };

    return (
        <View className={"flex h-screen items-center bg-light_primary dark:bg-dark_primary"}>
            <View className="py-4">
                <Heading text={t("verifyReset_heading")} />
            </View>
            <Subheading text={t("verifyReset_subheading")} />
            <DefaultButton text={t("verifyReset_btn")} onPress={handleLoginPress} />
        </View>
    )
};

export default VerifyPasswordReset;