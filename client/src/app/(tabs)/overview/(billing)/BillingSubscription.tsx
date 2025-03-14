import React, { useState, useEffect } from "react";
import { View, ScrollView, ActivityIndicator } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { getUserMemberships } from "@/src/services/user/userService";
import { useRouter } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { useTranslation } from "react-i18next";
import Heading from "@/src/components/textFields/Heading";

const BillingSubscription = () => {
  const router = useRouter();
  const { t } = useTranslation("billing");
  const [memberships, setMemberships] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchMemberships = async () => {
      try {
        const data = await getUserMemberships();
        setMemberships(data);
      } catch (error) {
        Toast.show({
          type: "error",
          text1: t("errorFetchingMemberships"),
          text2: t("errorMembershipData")
        });
      } finally {
        setLoading(false);
      }
    };

    fetchMemberships();
  }, []);

  // Filter memberships based on their status
  const activeMemberships = memberships.filter(m => m.status === "Active");
  const cancelledMemberships = memberships.filter(m => m.status === "Cancelled");
  const cancelledByClubMemberships = memberships.filter(m => m.status === "Cancelled by Club");

  if (loading) {
    return (
      <View className="flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary">
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      {memberships.length > 0 ? (
        <>
          {activeMemberships.length > 0 && (
            <PageNavigator
              title={t("active")}
              texts={activeMemberships.map(m => m.membership.name)}
              onPressFunctions={activeMemberships.map(m => () =>
                router.push(`/(tabs)/overview/(billing)/ManageSubscription?membership=${encodeURIComponent(JSON.stringify(m))}&start_datetime=${m.start_datetime}&end_datetime=${m.end_datetime}`)
              )}
              iconNames={activeMemberships.map(() => "event")}
            />
          )}

          {cancelledMemberships.length > 0 && (
            <PageNavigator
              title={t("cancelled")}
              texts={cancelledMemberships.map(m => m.membership.name)}
              onPressFunctions={cancelledMemberships.map(m => () =>
                router.push(`/(tabs)/overview/(billing)/ManageSubscription?membership=${encodeURIComponent(JSON.stringify(m))}&start_datetime=${m.start_datetime}&end_datetime=${m.end_datetime}`)
              )}
              iconNames={cancelledMemberships.map(() => "event")}
            />
          )}

          {cancelledByClubMemberships.length > 0 && (
            <PageNavigator
              title={t("cancelledByClub")}
              texts={cancelledByClubMemberships.map(m => m.membership.name)}
              onPressFunctions={cancelledByClubMemberships.map(m => () =>
                router.push(`/(tabs)/overview/(billing)/ManageSubscription?membership=${encodeURIComponent(JSON.stringify(m))}&start_datetime=${m.start_datetime}&end_datetime=${m.end_datetime}`)
              )}
              iconNames={cancelledByClubMemberships.map(() => "event")}
            />
          )}
        </>
      ) : (
        <View className="py-4">
          <Heading text={t("noMemberships")} />
        </View>
      )}
      <DefaultToast />
    </ScrollView>
  );
};

export default BillingSubscription;