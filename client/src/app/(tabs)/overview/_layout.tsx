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
        name="(clubs)/ClubOverview"
        options={{
          headerTitle: t("clubs_overview_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubCreate"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_create_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubCreateProgramm"
        options={{
          headerTitle: t("clubs_create_programm_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubCreateSession"
        options={{
          headerTitle: t("clubs_create_session_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManageEmployee"
        options={{
          headerTitle: t("clubs_manage_employee_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManagement"
        options={{
          headerTitle: t("clubs_management_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManageRoles"
        options={{
          headerTitle: t("clubs_manage_roles_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManageTrainer"
        options={{
          headerTitle: t("clubs_manage_trainer_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManagePrograms"
        options={{
          headerTitle: t("clubs_manage_programs_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubDelete"
        options={{
          headerTitle: t("clubs_delete_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubUpdate"
        options={{
          headerTitle: t("clubs_update_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManageFinance"
        options={{
          headerTitle: t("clubs_manage_finance_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubManageSessions"
        options={{
          headerTitle: t("clubs_manage_sessions_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubUpdateName"
        options={{
          headerTitle: t("clubs_update_name_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ClubUpdateAddress"
        options={{
          headerTitle: t("clubs_update_address_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ManageEmployee"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_employee_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/AddEmployee"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_employee_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/AddProgram"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_program_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ManageProgram"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_program_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/AddRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_role_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/ManageRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_role_header"),
        }}
      />
      <Stack.Screen
        name="(clubs)/InfoRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_info_role_header"),
        }}
      />
    </Stack>
  );
}
