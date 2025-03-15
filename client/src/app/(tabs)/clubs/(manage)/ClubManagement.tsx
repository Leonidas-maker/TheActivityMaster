import React from "react";
import { ScrollView } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

const ClubManagement = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    // Navigation handler functions
    const handleViewPagePress = () => {
        router.navigate(`/(tabs)/clubs/(view)/ClubPage?club_id=${club_id}`);
    };

    const handleClubCalendarPress = () => {
        router.navigate(`/(tabs)/clubs/(manage)/ClubCalendar?club_id=${club_id}`);
    };

    const handleManageEmployeePress = () => {
        router.navigate(`/(tabs)/clubs/(employee)/ClubManageEmployee?club_id=${club_id}`);
    };

    const handleManageProgramsPress = () => {
        router.navigate(`/(tabs)/clubs/(program)/ClubManagePrograms?club_id=${club_id}`);
    };

    const handleManageMembershipsPress = () => {
        router.navigate(`/(tabs)/clubs/(membership)/ClubManageMemberships?club_id=${club_id}`);
    };

    const handleManageRolesPress = () => {
        router.navigate(`/(tabs)/clubs/(role)/ClubManageRoles?club_id=${club_id}`);
    };

    const handleManageBookingSubscriptionPress = () => {
        router.navigate(`/(tabs)/clubs/(finance)/ClubManageFinance?club_id=${club_id}`);
    };

    const handleUpdatePress = () => {
        router.navigate(`/(tabs)/clubs/(manage)/ClubUpdate?club_id=${club_id}`);
    };

    const handleDeletePress = () => {
        router.navigate(`/(tabs)/clubs/(manage)/ClubDelete?club_id=${club_id}`);
    };

    const manageClubTitle = t("manageClub_navigator_title");

    // Create navigation items array based on permissions
    // Each item includes text, icon, and onPress function
    const navItems = [];

    // Always show the view page navigation
    navItems.push({
        text: t("club_view_page"),
        icon: "home",
        onPress: handleViewPagePress,
    });

    // Always show the club calendar navigation
    navItems.push({
        text: t("club_calendar"),
        icon: "calendar-month",
        onPress: handleClubCalendarPress,
    });

    // Conditionally add employee management navigation
    if (hasPermission("club_read_employees")) {
        navItems.push({
            text: t("club_manage_employee_btn"),
            icon: "badge",
            onPress: handleManageEmployeePress,
        });
    }

    // Conditionally add programs management navigation
    if (hasPermission("club_read_programs")) {
        navItems.push({
            text: t("club_manage_programs_btn"),
            icon: "category",
            onPress: handleManageProgramsPress,
        });
    }

    // Conditionally add memberships management navigation
    if (hasPermission("club_read_memberships")) {
        navItems.push({
            text: t("club_manage_memberships_btn"),
            icon: "card-membership",
            onPress: handleManageMembershipsPress,
        });
    }

    // Conditionally add roles management navigation
    if (hasPermission("club_read_roles")) {
        navItems.push({
            text: t("club_manage_roles_btn"),
            icon: "manage-accounts",
            onPress: handleManageRolesPress,
        });
    }

    // Conditionally add update navigation for club data
    if (hasPermission("club_update_club_data") && hasPermission("club_delete_club_data")) {
        navItems.push({
            text: t("club_update_btn"),
            icon: "edit",
            onPress: handleUpdatePress,
        });
    }

    // Conditionally add manage booking subscription navigation for confidential club data
    if (hasPermission("club_read_club_confidential_data")) {
        navItems.push({
            text: t("club_manage_booking_subscription"),
            icon: "account-balance-wallet",
            onPress: handleManageBookingSubscriptionPress,
        });
    }

    // Conditionally add delete navigation for club data
    if (hasPermission("club_owner")) {
        navItems.push({
            text: t("club_delete_btn"),
            icon: "delete",
            onPress: handleDeletePress,
        });
    }

    // Separate the properties into arrays required by PageNavigator
    const createClubTexts = navItems.map(item => item.text);
    const createClubIcons = navItems.map(item => item.icon);
    const onPressCreateClubFunctions = navItems.map(item => item.onPress);

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
