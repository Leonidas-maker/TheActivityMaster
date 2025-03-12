import React from "react";
import { ScrollView, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ClubManagement = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();

    const handleViewPagePress = () => {
        //TODO: Implement
        console.log("View page");
    };
    const handleManageEmployeePress = () => {
        router.navigate(`/(tabs)/clubs/(employee)/ClubManageEmployee?club_id=${club_id}`);
    };
    const handleManageProgramsPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/ClubManagePrograms?club_id=${club_id}`);
    };
    const handleManageRolesPress = () => {
        router.navigate(`/(tabs)/clubs/(role)/ClubManageRoles?club_id=${club_id}`);
    };
    const handleManageBookingSubscriptionPress = () => {
        router.navigate(`/(tabs)/clubs/(finance)/ClubManageFinance?club_id=${club_id}`);
    };
    const handleUpdatePress = () => {
        router.navigate(`/(tabs)/clubs/ClubUpdate?club_id=${club_id}`);
    };
    const handleDeletePress = () => {
        router.navigate(`/(tabs)/clubs/ClubDelete?club_id=${club_id}`);
    };
    const handleManageMembershipsPress = () => {
        router.navigate(`/(tabs)/clubs/(membership)/ClubManageMemberships?club_id=${club_id}`);
    };

    const manageClubTitle = t("manageClub_navigator_title");
    
    const createClubTexts = [t("club_view_page"), t("club_manage_employee_btn"), t("club_manage_programs_btn"), t("club_manage_memberships_btn"), t("club_manage_roles_btn"), t("club_manage_booking_subscription"), t("club_update_btn"), t("club_delete_btn")];
    const createClubIcons = ["home", "badge", "category", "card-membership", "manage-accounts", "account-balance-wallet", "edit", "delete"];
    const onPressCreateClubFunctions = [handleViewPagePress, handleManageEmployeePress, handleManageProgramsPress, handleManageMembershipsPress, handleManageRolesPress, handleManageBookingSubscriptionPress, handleUpdatePress, handleDeletePress];

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={manageClubTitle}
                texts={createClubTexts}
                iconNames={createClubIcons}
                onPressFunctions={onPressCreateClubFunctions}
            />
        </ScrollView>
    );
};

export default ClubManagement;