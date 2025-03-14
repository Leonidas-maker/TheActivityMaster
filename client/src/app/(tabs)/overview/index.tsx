// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { useCallback, useState } from "react";
import { View, ScrollView, Linking } from "react-native";
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
import { asyncRemoveData, asyncLoadData } from "@/src/services/asyncStorageService";
import { logout } from "@/src/services/auth/tokenService";
import { secureRemoveData } from "@/src/services/secureStorageService";
import { getUserData } from "@/src/services/user/userService";
import { getGlobalLogout } from "@/src/provider/AuthContextProvider";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const OverviewHome: React.FC = () => {
  // ~~~~~~~~~~~ Define navigator ~~~~~~~~~~ //
  const router = useRouter();
  const { t } = useTranslation("overview");

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isVerified, setIsVerified] = useState(false);

  const handleLogoutPress = async () => {
    await logout().then(() => {
      asyncRemoveData("isLoggedIn");
      secureRemoveData("access_token");
      secureRemoveData("refresh_token");
      asyncRemoveData("isAdmin");
      asyncRemoveData("isVerified");
      const globalLogout = getGlobalLogout();
      if (globalLogout) {
        globalLogout();
      }
      router.navigate("/(tabs)");
    });
  };

  // ~~~~~ Check login status on page focus ~~~~~ //
  useFocusEffect(
    useCallback(() => {
      // Async function to check if user is logged in
      async function checkLoginStatus() {
        try {
          const loginStatus = await asyncLoadData("isLoggedIn");
          const loggedIn = loginStatus === "true";
          setIsLoggedIn(loggedIn);
          // Once login status is updated, immediately check verification
          if (loggedIn) {
            await checkVerifiedStatus();
          }
        } catch (error) {
          setIsLoggedIn(false);
        }
      }
      async function checkAdminStatus() {
        try {
          const adminStatus = await asyncLoadData("isAdmin");
          setIsAdmin(adminStatus === "true");
        } catch (error) {
          setIsAdmin(false);
        }
      }
      async function checkVerifiedStatus() {
        try {
          const response = await getUserData();
          setIsVerified(response.identity_verified);
        } catch (error) {
          setIsVerified(false);
        }
      }
      checkLoginStatus();
      checkAdminStatus();
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

  const handleBookedPress = () => {
    router.navigate("/(tabs)/overview/(billing)/BillingBooked");
  };

  const billingTitle = t("pageNavigator_title3");

  const onPressBillingFunctions = [handleSubscriptionPress, handleBookedPress, handleHistoryPress];

  const billingTexts = [t("billing_subscription_btn"), t("billing_booked_btn"), t("billing_history_btn")];

  const billingIconNames = ["payments", "shopping-bag", "receipt-long"];

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
  // =================== AdminNavigator =================== //
  // ====================================================== //
  const handleIdentityOverviewPress = () => {
    router.navigate("/(tabs)/overview/(admin)/AdminIdentityOverview");
  };

  const adminTitle = t("pageNavigator_title4");

  const onPressAdminFunctions = [handleIdentityOverviewPress];

  const adminTexts = [t("admin_identity_overview_btn")];

  const adminIconNames = ["people"];

  // ====================================================== //
  // =================== InfoNavigator ==================== //
  // ====================================================== //
  const handleBugReportPress = () => {
    router.navigate("/(tabs)/overview/(info)/BugReport");
  }

  const handleImprintPress = () => {
    router.navigate("/(tabs)/overview/(info)/Imprint");
  }

  const handleLicensesPress = () => {
    router.navigate("/(tabs)/overview/(info)/Licenses");
  }

  const handleResponsibleDisclosurePress = () => {
    router.navigate("/(tabs)/overview/(info)/ResponsibleDisclosure");
  }

  const handleSupportPress = () => {
    router.navigate("/(tabs)/overview/(info)/Support");
  }

  const handleTermsPress = () => {
    router.navigate("/(tabs)/overview/(info)/Terms");
  }

  const handleGitLabPress = () => {
    Linking.openURL("https://gitlab.com/themastercollection/theactivitymaster");
  }

  const handleGitHubPress = () => {
    Linking.openURL("https://github.com/Leonidas-maker/TheActivityMaster");
  }

  const handlePrivacyPress = () => {
    Linking.openURL("https://gitlab.com/themastercollection/TheActivityMaster/-/wikis/Privacy-Policy");
  }

  const onInfoPressFunctions = [handleGitLabPress, handleGitHubPress, handleBugReportPress, handleResponsibleDisclosurePress, handleSupportPress, handleImprintPress, handleTermsPress, handlePrivacyPress, handleLicensesPress];
  
  const infoTitle = t("pageNavigator_title6");

  const infoTexts = [t("gitlab_btn"), t("github_btn"), t("bug_report_btn"), t("responsible_disclosure_btn"), t("support_btn"), t("imprint_btn"), t("terms_of_service_btn"), t("privacy_policy_btn"), t("licenses_btn")];

  const infoIconNames = ["web", "web", "bug-report", "security", "support", "description", "gavel", "lock", "article"];

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
      {isAdmin && isLoggedIn && (<PageNavigator
        title={adminTitle}
        onPressFunctions={onPressAdminFunctions}
        texts={adminTexts}
        iconNames={adminIconNames}
      />)}
      {/* <PageNavigator
        title={devTitle}
        onPressFunctions={onPressDevFunctions}
        texts={devTexts}
        iconNames={devIconNames}
      /> */}
      <PageNavigator
        title={infoTitle}
        onPressFunctions={onInfoPressFunctions}
        texts={infoTexts}
        iconNames={infoIconNames}
      />
      {/* <DefaultButton text={t("clear_storage_btn")} onPress={() => clearAllStorage()} /> */}
      {isLoggedIn && (
        <View className="justify-center items-center my-2">
          <SecondaryButton text={t("logout_btn")} onPress={handleLogoutPress} />
        </View>
      )}
      <View className="justify-center items-center my-2">
        <DefaultText text={t("app_version") + `: ${expo.version} ❤️`} />
      </View>
    </ScrollView>
  );
};

export default OverviewHome;
