import React, { useCallback, useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useFocusEffect, useNavigation } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { getEmployees } from "@/src/services/club/employeeService";
import Icon from "react-native-vector-icons/MaterialIcons";

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

    const [employees, setEmployees] = useState<EmployeesResponse>({});

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

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(employee)/AddEmployee?club_id=${club_id}`);
    };

    useEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <Pressable onPress={handleAddPress}>
                    <Icon
                        name="add"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    // Combine employees from all roles into one array with proper type annotation
    const allEmployees: Employee[] = [];
    Object.keys(employees).forEach((role) => {
        if (Array.isArray(employees[role])) {
            allEmployees.push(...employees[role]);
        }
    });

    // Map employee objects to their display name, onPress functions and icon names
    const employeeNames = allEmployees.map(
        (emp) => `${emp.first_name} ${emp.last_name}`
    );

    const employeeOnPress = allEmployees.map((emp) => () => {
        router.navigate(`/(tabs)/clubs/(employee)/ManageEmployee?user_id=${emp.id}&club_id=${club_id}`);
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