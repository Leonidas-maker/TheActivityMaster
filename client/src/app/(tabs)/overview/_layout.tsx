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
    </Stack>
  );
}
