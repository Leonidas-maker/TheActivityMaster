import React from "react"
import { View } from "react-native"
import { useTranslation } from "react-i18next"
import DefaultButton from "@/src/components/buttons/DefaultButton"
import { useRouter } from "expo-router"
import Heading from "@/src/components/textFields/Heading"
import Subheading from "@/src/components/textFields/Subheading"

const VerifyMail = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    return (
        <View className={"flex h-screen items-center bg-light_primary dark:bg-dark_primary"}>
            <View className="py-4">
                <Heading text={t("verifyMail_heading")} />
            </View>
            <Subheading text={t("verifyMail_subheading")} />
            <DefaultButton text={t("verifyMail_btn")} onPress={() => router.navigate("/auth")} />
        </View>
    )
}

export default VerifyMail;