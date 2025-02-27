import React from "react";
import { ScrollView, View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

const ClubManagementEmployees = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="items-center">
                <Heading text={t("manageClub")} />
                <DefaultTextFieldInput placeholder={t("clubName")} />
                <DefaultTextFieldInput placeholder={t("clubDescription")} />
                <DefaultButton text={t("manage")} onPress={() => console.log("Pressed")} />
            </View>
        </ScrollView>
    );
};

export default ClubManagementEmployees;