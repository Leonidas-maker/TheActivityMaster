import React from "react";
import { ScrollView, View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ClubUpdate = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    const { club_id } = useLocalSearchParams();

    const onPressUpdateName = () => {
        router.navigate(`/(tabs)/clubs/(manage)/ClubUpdateName?club_id=${club_id}`);
    };

    const onPressUpdateAddress = () => {
        router.navigate(`/(tabs)/clubs/(manage)/ClubUpdateAddress?club_id=${club_id}`);
    };

    const onPressFunctions = [onPressUpdateName, onPressUpdateAddress];

    const texts = [t("club_update_name_btn"), t("club_update_address_btn")];

    const iconNames = ["edit", "edit"];

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator 
                title={t("club_update_navigator_title")}
                iconNames={iconNames}
                onPressFunctions={onPressFunctions}
                texts={texts}
            />
        </ScrollView>
    );
}

export default ClubUpdate;