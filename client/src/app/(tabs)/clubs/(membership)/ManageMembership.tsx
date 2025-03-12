import React from "react";
import { ScrollView, View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ManageMembership = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id, membership_id } = useLocalSearchParams();

    const handleMembershipUpdatePress = () => {
        router.navigate(`/(tabs)/clubs/(membership)/UpdateMembership?club_id=${club_id}&membership_id=${membership_id}`);
    }

    const handleMembershipAccessOverviewPress = () => {
        router.navigate(`/(tabs)/clubs/(membership)/MembershipAccessOverview?club_id=${club_id}&membership_id=${membership_id}`);
    }

    const handleDeleteMembershipPress = () => {
        router.navigate(`/(tabs)/clubs/(membership)/DeleteMembership?club_id=${club_id}&membership_id=${membership_id}`);
    }

    const pressFunctions = [handleMembershipAccessOverviewPress, handleMembershipUpdatePress, handleDeleteMembershipPress];

    const navigatorTexts = [t("membershipAccessOverview"), t("updateMembership"), t("deleteMembership")];

    const navigatorIcons = ["add-circle", "edit", "delete"];

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={t("manageMembership")}
                onPressFunctions={pressFunctions}
                texts={navigatorTexts}
                iconNames={navigatorIcons}
            />
        </ScrollView>
    );
}

export default ManageMembership;