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
          headerTitle: t("clubs_tab"),
        }}
      />

      <Stack.Screen
        name="ClubManagement"
        options={{
          headerTitle: t("clubs_management_header"),
        }}
      />
      <Stack.Screen
        name="ClubCreate"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_create_header"),
        }}
      />
      <Stack.Screen
        name="(employee)/ClubManageEmployee"
        options={{
          headerTitle: t("clubs_manage_employee_header"),
        }}
      />
      <Stack.Screen
        name="(role)/ClubManageRoles"
        options={{
          headerTitle: t("clubs_manage_roles_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ClubManageTrainer"
        options={{
          headerTitle: t("clubs_manage_trainer_header"),
        }}
      />
      <Stack.Screen
        name="(program)/ClubManagePrograms"
        options={{
          headerTitle: t("clubs_manage_programs_header"),
        }}
      />
      <Stack.Screen
        name="ClubDelete"
        options={{
          headerTitle: t("clubs_delete_header"),
        }}
      />
      <Stack.Screen
        name="ClubUpdate"
        options={{
          headerTitle: t("clubs_update_header"),
        }}
      />
      <Stack.Screen
        name="(finance)/ClubManageFinance"
        options={{
          headerTitle: t("clubs_manage_finance_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ClubManageSessions"
        options={{
          headerTitle: t("clubs_manage_sessions_header"),
        }}
      />
      <Stack.Screen
        name="ClubUpdateName"
        options={{
          headerTitle: t("clubs_update_name_header"),
        }}
      />
      <Stack.Screen
        name="ClubUpdateAddress"
        options={{
          headerTitle: t("clubs_update_address_header"),
        }}
      />
      <Stack.Screen
        name="(employee)/ManageEmployee"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_employee_header"),
        }}
      />
      <Stack.Screen
        name="(employee)/AddEmployee"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_employee_header"),
        }}
      />
      <Stack.Screen
        name="(program)/AddProgram"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_program_header"),
        }}
      />
      <Stack.Screen
        name="(program)/ManageProgram"
        options={{
          headerTitle: t("clubs_manage_program_header"),
        }}
      />
      <Stack.Screen
        name="(role)/AddRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_role_header"),
        }}
      />
      <Stack.Screen
        name="(role)/ManageRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_role_header"),
        }}
      />
      <Stack.Screen
        name="(role)/InfoRole"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_info_role_header"),
        }}
      />
      <Stack.Screen
        name="(program)/UpdateProgram"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_update_program_header"),
        }}
      />
      <Stack.Screen
        name="(session)/AddSession"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_session_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ManageSession"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_session_header"),
        }}
      />
    </Stack>
  );
}
