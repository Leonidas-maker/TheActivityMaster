import { Stack } from "expo-router";
import React, { useEffect, useState } from "react";
import { useColorScheme } from "nativewind";
import { useTranslation } from "react-i18next";

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
          headerTitle: t("settings_multi_factor_header"),
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
    </Stack>
  );
}
