import React, { useCallback, useState, useEffect } from "react";
import { ScrollView, useColorScheme, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useFocusEffect, useNavigation } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { getEmployees } from "@/src/services/club/employeeService";
import Icon from "react-native-vector-icons/MaterialIcons";
import Toast from "react-native-toast-message";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

interface Employee {
    first_name: string;
    last_name: string;
    email: string;
    id: string;
}

type EmployeesResponse = Record<string, Employee[]>;

const ClubManagementEmployees = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    const [employees, setEmployees] = useState<EmployeesResponse>({});

    // Fetch employees on focus
    useFocusEffect(
        useCallback(() => {
            const fetchEmployees = async () => {
                try {
                    const data = await getEmployees(club_id);
                    setEmployees(data);
                } catch (error) {
                    console.error("Error during fetchEmployees call:", error);
                }
            };
            fetchEmployees();
        }, [club_id])
    );

    // Track light theme
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // Handle adding a new employee
    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(employee)/AddEmployee?club_id=${club_id}`);
    };

    // Set headerRight only if user has "club_create_employees" permission
    useEffect(() => {
        navigation.setOptions({
            headerRight: () =>
                hasPermission("club_create_employees") ? (
                    <Pressable onPress={handleAddPress}>
                        <Icon
                            name="add"
                            size={30}
                            color={iconColor}
                            style={{ marginLeft: "auto", marginRight: 15 }}
                        />
                    </Pressable>
                ) : null
        });
    }, [navigation, iconColor, hasPermission]);

    // Combine employees from all roles into one array
    const allEmployees: Employee[] = [];
    Object.keys(employees).forEach((role) => {
        if (Array.isArray(employees[role])) {
            allEmployees.push(...employees[role]);
        }
    });

    // Prepare display names for employees
    const employeeNames = allEmployees.map(
        (emp) => `${emp.first_name} ${emp.last_name}`
    );

    // Map each employee to its onPress function with permission check for "club_update_employees"
    const employeeOnPress = allEmployees.map((emp) => () => {
        if (!hasPermission("club_update_employees")) {
            // Show Toast message if permission is missing
            Toast.show({
                type: "info",
                text1: t("permissionError"),
                text2: t("permissionErrorDescription"),
            });
        } else {
            // Navigate if permission exists
            router.navigate(`/(tabs)/clubs/(employee)/ManageEmployee?user_id=${emp.id}&club_id=${club_id}`);
        }
    });

    const employeeIconNames = allEmployees.map(() => "person");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={t("club_employee_overview_navigator")}
                texts={employeeNames}
                onPressFunctions={employeeOnPress}
                iconNames={employeeIconNames}
            />
        </ScrollView>
    );
};

export default ClubManagementEmployees;
