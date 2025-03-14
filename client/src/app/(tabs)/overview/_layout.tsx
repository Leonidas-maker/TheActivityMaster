import { Stack } from "expo-router";
import React, { useEffect, useState } from "react";
import { useColorScheme } from "nativewind";
import { useTranslation } from "react-i18next";
import { Alert, Button } from "react-native";

export default function OverviewLayout() {
  const [isLight, setIsLight] = useState(false);
  const { t } = useTranslation("router");

  const { colorScheme } = useColorScheme();

  useEffect(() => {
    if (colorScheme === "light") {
      setIsLight(true);
    } else {
      setIsLight(false);
    }
  }, [colorScheme]);

  const backgroundColor = isLight ? "#E8EBF7" : "#1E1E24";
  const headerTintColor = isLight ? "#171717" : "#E0E2DB";

  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerStyle: {
          backgroundColor: backgroundColor,
        },
        headerTintColor: headerTintColor,
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          headerTitle: t("more_tab"),
        }}
      />

      <Stack.Screen
        name="(settings)/Settings"
        options={{
          headerTitle: t("settings_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsTheme"
        options={{
          headerTitle: t("settings_theme_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsLanguage"
        options={{
          headerTitle: t("settings_language_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsUser"
        options={{
          headerTitle: t("settings_user_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsSecurity"
        options={{
          headerTitle: t("settings_security_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsNotifications"
        options={{
          headerTitle: t("settings_notifications_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangeAddress"
        options={{
          headerTitle: t("settings_change_address_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangeEmail"
        options={{
          headerTitle: t("settings_change_email_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangeEmailInfo"
        options={{
          gestureEnabled: false,
          presentation: "modal",
          headerTitle: t("settings_change_email_info_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangeUsername"
        options={{
          headerTitle: t("settings_change_username_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangePassword"
        options={{
          headerTitle: t("settings_change_password_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsDeleteUser"
        options={{
          headerTitle: t("settings_delete_user_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsLogout"
        options={{
          headerTitle: t("settings_logout_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsMultiFactor"
        options={{
          presentation: "modal",
          headerTitle: t("settings_multi_factor_header"),
          gestureEnabled: false,
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsChangeName"
        options={{
          headerTitle: t("settings_name_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsActivateMFA"
        options={{
          headerTitle: t("settings_activate_mfa_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsDeactivateMFA"
        options={{
          headerTitle: t("settings_deactivate_mfa_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsVerificationStatus"
        options={{
          headerTitle: t("settings_verification_status_header"),
        }}
      />
      <Stack.Screen
        name="(settings)/SettingsSubmitVerification"
        options={{
          headerTitle: t("settings_submit_verification_header"),
        }}
      />
      <Stack.Screen
        name="(billing)/BillingHistory"
        options={{
          headerTitle: t("billing_history_header"),
        }}
      />
      <Stack.Screen
        name="(billing)/BillingSubscription"
        options={{
          headerTitle: t("billing_subscription_header"),
        }}
      />
      <Stack.Screen
        name="(billing)/BillingBooked"
        options={{
          headerTitle: t("billing_booked_header"),
        }}
      />
      <Stack.Screen
        name="(admin)/AdminIdentityOverview"
        options={{
          headerTitle: t("admin_identity_overview_header"),
        }}
      />
      <Stack.Screen
        name="(admin)/AdminIdentityApprove"
        options={{
          headerTitle: t("admin_identity_approve_header"),
        }}
      />
      <Stack.Screen
        name="(info)/BugReport"
        options={{
          headerTitle: t("bug_report_header"),
        }}
      />
      <Stack.Screen
        name="(info)/Licenses"
        options={{
          headerTitle: t("licenses_header"),
        }}
      />
      <Stack.Screen
        name="(info)/Terms"
        options={{
          headerTitle: t("terms_of_service_header"),
        }}
      />
      <Stack.Screen
        name="(info)/Imprint"
        options={{
          headerTitle: t("imprint_header"),
        }}
      />
      <Stack.Screen
        name="(info)/ResponsibleDisclosure"
        options={{
          headerTitle: t("responsible_disclosure_header"),
        }}
      />
      <Stack.Screen
        name="(info)/Support"
        options={{
          headerTitle: t("support_header"),
        }}
      />
    </Stack>
  );
}
