// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { useCallback, useState } from "react";
import { View, ScrollView } from "react-native";
import { expo } from "@/app.json";
import { Link, useFocusEffect, useRouter } from "expo-router";
import { clearAllStorage } from "@/src/services/clearStorage";
import { useTranslation } from "react-i18next";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import PageNavigator from '@/src/components/pageNavigator/PageNavigator';
import ProfileView from "@/src/components/userComponents/ProfileView";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import { axiosInstance } from "@/src/services/api";
import { asyncRemoveData, asyncLoadData } from "@/src/services/asyncStorageService";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const OverviewHome: React.FC = () => {
  // ~~~~~~~~~~~ Define navigator ~~~~~~~~~~ //
  const router = useRouter();
  const { t } = useTranslation("overview");

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogoutPress = async () => {
    axiosInstance.delete("/auth/logout").then(() => {
      asyncRemoveData("isLoggedIn");
      router.navigate("/(tabs)");
    });
  };

  // ~~~~~ Check login status on page focus ~~~~~ //
  useFocusEffect(
    useCallback(() => {
      // Async function to check if user is logged in
      async function checkLoginStatus() {
        try {
          // Try loading the login status from async storage
          const loginStatus = await asyncLoadData("isLoggedIn");
          // If a truthy value is returned, user is logged in, otherwise not logged in.
          setIsLoggedIn(!!loginStatus);
        } catch (error) {
          // In case of error, consider user not logged in.
          setIsLoggedIn(false);
        }
      }
      checkLoginStatus();
    }, [])
  );

  // ====================================================== //
  // ================== SettingsNavigator ================= //
  // ====================================================== //
  const handleSettingsPress = () => {
    router.navigate("/(tabs)/overview/(settings)/Settings");
  };

  const moduleTitle = t("pageNavigator_title1");

  const onPressModuleFunctions = [handleSettingsPress];

  const moduleTexts = [t("settings_btn")];

  const moduleIconNames = ["settings"];

  // ====================================================== //
  // ================== BillingNavigator ================== //
  // ====================================================== //
  const handleHistoryPress = () => {
    router.navigate("/(tabs)/overview/(billing)/BillingHistory");
  };

  const handleSubscriptionPress = () => {
    router.navigate("/(tabs)/overview/(billing)/BillingSubscription");
  };

  const billingTitle = t("pageNavigator_title3");

  const onPressBillingFunctions = [handleSubscriptionPress, handleHistoryPress];

  const billingTexts = [t("billing_subscription_btn"), t("billing_history_btn")];

  const billingIconNames = ["payments", "receipt-long"];

  // ====================================================== //
  // ==================== DevNavigator ==================== //
  // ====================================================== //
  const handleLoginPress = () => {
    router.navigate("/auth");
  };

  const handleSignupPress = () => {
    router.navigate("/auth/SignUp");
  }

  const devTitle = t("pageNavigator_title2");

  const onPressDevFunctions = [handleLoginPress, handleSignupPress];

  const devTexts = [t("login_btn"), t("signup_btn")];

  const devIconNames = ["login", "note-add"];

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  // Returns the navigators and the current app version
  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <ProfileView />
      <PageNavigator
        title={moduleTitle}
        onPressFunctions={onPressModuleFunctions}
        texts={moduleTexts}
        iconNames={moduleIconNames}
      />
      {isLoggedIn && (<PageNavigator
        title={billingTitle}
        onPressFunctions={onPressBillingFunctions}
        texts={billingTexts}
        iconNames={billingIconNames}
      />)}
      {/* <PageNavigator
        title={devTitle}
        onPressFunctions={onPressDevFunctions}
        texts={devTexts}
        iconNames={devIconNames}
      /> */}
      <View className="justify-center items-center my-2">
        <DefaultButton text={t("clear_storage_btn")} onPress={() => clearAllStorage()} />
        {isLoggedIn && (
          <SecondaryButton text={t("logout_btn")} onPress={handleLogoutPress} />
        )}
      </View>
      <View className="justify-center items-center my-2">
        <DefaultText text={t("app_version") + `: ${expo.version} ❤️`} />
      </View>
    </ScrollView>
  );
};

export default OverviewHome;
