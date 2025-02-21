import React from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

const AdminIdentityOverview = async () => {
    const { t } = useTranslation("admin");
    const router = useRouter();

    return (
        <View className="flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text={t("test_text")} />
        </View>
    );
};

export default AdminIdentityOverview;