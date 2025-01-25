import React, { useEffect } from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import generateFingerprint from "@/src/fingerprint/Fingerprint";
import { useTranslation } from "react-i18next";

export default function Tab() {
    useEffect(() => {
        generateFingerprint();
    }, []);

    const { t } = useTranslation("discover");

    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text={t("test_text")} />
        </View>
    );
};