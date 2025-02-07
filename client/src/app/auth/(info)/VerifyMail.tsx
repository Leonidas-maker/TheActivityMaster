import React from "react"
import { View } from "react-native"
import DefaultText from "@/src/components/textFields/DefaultText"
import { useTranslation } from "react-i18next"
import DefaultButton from "@/src/components/buttons/DefaultButton"
import { useRouter } from "expo-router"

const VerifyMail = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text={t("verifyMail_text")} />
            <DefaultButton text={t("verifyMail_btn")} onPress={() => router.navigate("/auth")} />
        </View>
    )
}

export default VerifyMail;