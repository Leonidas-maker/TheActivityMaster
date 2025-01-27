import React, { useState, useEffect } from "react";
import { View, ScrollView } from "react-native";
import { useTranslation } from 'react-i18next';
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { useRouter } from "expo-router";

const SignUp: React.FC = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text={t("test_text2")} />
            <DefaultButton text={t("test_text")} onPress={() => router.push("/auth")} />
        </View>
    );
};

export default SignUp;
