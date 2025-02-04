import React from "react"
import { View } from "react-native"
import DefaultText from "@/src/components/textFields/DefaultText"
import { useTranslation } from "react-i18next"

const VerifyMail = () => {
    const { t } = useTranslation("auth")

    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text={t("test_text")} />
        </View>
    )
}

export default VerifyMail;