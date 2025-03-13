import { Stack } from "expo-router";
import React, { useEffect, useState } from "react";
import { useColorScheme } from "nativewind";
import { useTranslation } from "react-i18next";
import { Alert, Button } from "react-native";

export default function SearchLayout() {
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
          headerTitle: t("search_tab"),
        }}
      />

      <Stack.Screen
        name="(view)/ClubPage"
        options={{
          headerTitle: t("clubs_view_page_header"),
        }}
      />
      <Stack.Screen
        name="(view)/MembershipPage"
        options={{
          headerTitle: t("clubs_membership_page_header"),
        }}
      />
      <Stack.Screen
        name="(view)/ProgramPage"
        options={{
          headerTitle: t("clubs_program_page_header"),
        }}
      />
      <Stack.Screen
        name="(view)/SessionPage"
        options={{
          headerTitle: t("clubs_session_page_header"),
        }}
      />
    </Stack>
  );
}
