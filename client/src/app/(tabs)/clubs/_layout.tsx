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
        name="(manage)/ClubManagement"
        options={{
          headerTitle: t("clubs_management_header"),
        }}
      />
      <Stack.Screen
        name="(manage)/ClubCreate"
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
        name="(program)/ClubManagePrograms"
        options={{
          headerTitle: t("clubs_manage_programs_header"),
        }}
      />
      <Stack.Screen
        name="(manage)/ClubDelete"
        options={{
          headerTitle: t("clubs_delete_header"),
        }}
      />
      <Stack.Screen
        name="(manage)/ClubUpdate"
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
        name="(manage)/ClubUpdateName"
        options={{
          headerTitle: t("clubs_update_name_header"),
        }}
      />
      <Stack.Screen
        name="(manage)/ClubUpdateAddress"
        options={{
          headerTitle: t("clubs_update_address_header"),
        }}
      />
      <Stack.Screen
        name="(manage)/ClubCalendar"
        options={{
          headerTitle: t("clubs_calendar_header"),
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
          headerTitle: t("clubs_manage_session_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ManageCourse"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_course_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ManageEvent"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_event_header"),
        }}
      />
      <Stack.Screen
        name="(session)/ManageOccurrence"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_occurence_header"),
        }}
      />
      <Stack.Screen
        name="(program)/ManageTrainer"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_trainer_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/AddMembership"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_membership_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/ManageMembership"
        options={{
          headerTitle: t("clubs_manage_membership_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/ClubManageMemberships"
        options={{
          headerTitle: t("clubs_manage_memberships_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/UpdateMembership"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_update_membership_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/MembershipAccessOverview"
        options={{
          headerTitle: t("clubs_membership_access_overview_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/AddProgramMembershipAccess"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_add_program_membership_access_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/ManageProgramMembershipAccess"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_manage_program_membership_access_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/DeleteMembership"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_delete_membership_header"),
        }}
      />
      <Stack.Screen
        name="(membership)/SubscriberOverview"
        options={{
          presentation: "modal",
          headerTitle: t("clubs_subscriber_overview_header"),
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
        name="(view)/EventPage"
        options={{
          headerTitle: t("clubs_event_page_header"),
        }}
      />
      <Stack.Screen
        name="(view)/CoursePage"
        options={{
          headerTitle: t("clubs_course_page_header"),
        }}
      />
      <Stack.Screen
        name="(view)/BookingPage"
        options={{
          headerTitle: t("clubs_booking_page_header"),
        }}
      />
    </Stack>
  );
}
