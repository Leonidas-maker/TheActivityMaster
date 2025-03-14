import React from "react";
import { ScrollView } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

const ManageMembership = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id, membership_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    // Create lists for navigator options
    const pressFunctions = [];
    const navigatorTexts = [];
    const navigatorIcons = [];

    // Always add Membership Access Overview option
    pressFunctions.push(() =>
        router.navigate(`/(tabs)/clubs/(membership)/MembershipAccessOverview?club_id=${club_id}&membership_id=${membership_id}`)
    );
    navigatorTexts.push(t("membershipAccessOverview"));
    navigatorIcons.push("add-circle");

    // Always add Subscriber Overview option
    pressFunctions.push(() =>
        router.navigate(`/(tabs)/clubs/(membership)/SubscriberOverview?club_id=${club_id}&membership_id=${membership_id}`)
    );
    navigatorTexts.push(t("subscriberOverview"));
    navigatorIcons.push("subscriptions");

    // Conditionally add Update Membership option if the permission is present
    if (hasPermission("club_update_memberships")) {
        pressFunctions.push(() =>
            router.navigate(`/(tabs)/clubs/(membership)/UpdateMembership?club_id=${club_id}&membership_id=${membership_id}`)
        );
        navigatorTexts.push(t("updateMembership"));
        navigatorIcons.push("edit");
    }

    // Conditionally add Delete Membership option if the permission is present
    if (hasPermission("club_delete_memberships")) {
        pressFunctions.push(() =>
            router.navigate(`/(tabs)/clubs/(membership)/DeleteMembership?club_id=${club_id}&membership_id=${membership_id}`)
        );
        navigatorTexts.push(t("deleteMembership"));
        navigatorIcons.push("delete");
    }

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
};

export default ManageMembership;
