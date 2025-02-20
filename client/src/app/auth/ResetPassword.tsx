import React from "react";
import { View } from "react-native";
import { useTranslation } from "react-i18next";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useRouter } from "expo-router";

const ResetPassword = () => {
    const { t } = useTranslation();
    const router = useRouter();

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the reset password settings page" />
        </View>
    );
};

export default ResetPassword;