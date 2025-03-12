import React, { useState, useEffect } from "react";
import { ScrollView, View, Platform, useColorScheme, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback, Alert, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Icon from "react-native-vector-icons/MaterialIcons";
import Dropdown from "@/src/components/dropdown/Dropdown";
import { getUserData } from "@/src/services/user/userService";
import { getEmployee, updateEmployee, deleteEmployee } from "@/src/services/club/employeeService";
import { getClubRoles } from "@/src/services/club/roleService";
import Subheading from "@/src/components/textFields/Subheading";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

interface UserData {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    address: {
        street: string;
        postal_code: string;
        city: string;
        state: string;
        country: string;
    };
    id: string;
    is_newsletter_subscribed: boolean;
    methods_2fa: any[];
    identity_verified: boolean;
}

interface EmployeeData {
    first_name: string;
    last_name: string;
    email: string;
    id: string;
    role_name: string;
    role_level: number;
    program_assignments: any[];
}

interface Role {
    id: number;
    level: number;
    name: string;
    description: string;
    permissions: {
        name: string;
        description: string;
    }[];
}

const ManageEmployee = () => {
    const { t } = useTranslation("clubs");
    const router = useRouter();
    const navigation = useNavigation();
    const { user_id, club_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // States to hold user and employee data
    const [user, setUser] = useState<UserData | null>(null);
    const [employee, setEmployee] = useState<EmployeeData | null>(null);

    const [roleOptions, setRoleOptions] = useState<{ key: string; value: string }[]>([]);
    const [selectedRoleLevel, setSelectedRoleLevel] = useState("");

    // Fetch user and employee data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const userData = await getUserData();
                const employeeData = await getEmployee(club_id, user_id);
                setUser(userData);
                setEmployee(employeeData);

                const data: Role[] = await getClubRoles(club_id);
                // Filter out the role with level 10 (only one owner allowed)
                const formattedRoles = data
                    .filter((role: Role) => role.level !== 0) // Exclude role with level 10
                    .map((role: Role) => ({
                        key: role.level.toString(), // Convert level to string for the dropdown
                        value: role.name,
                    }));
                setRoleOptions(formattedRoles);

            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };
        fetchData();
    }, []);

    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleDeletePress = () => {
        Alert.alert(t("delete_employee_alert_title"), t("delete_employee_alert_text"), [
            {
                text: t("cancel_btn"),
                style: "cancel",
            },
            {
                text: t("confirm_btn"),
                onPress: () => deleteEmployeeHandler(),
            },
        ]);
    };

    const deleteEmployeeHandler = async () => {
        await deleteEmployee(club_id, user_id);

        router.dismiss();
    }

    const handleRoleChangePress = async () => {
        if (Number(selectedRoleLevel) === employee?.role_level) {
            Toast.show({
                type: "error",
                text1: t("employee_same_role_toast_error"),
                text2: t("employee_same_role_toast_error_description"),
            });
            return;
        }

        try {
            await updateEmployee(club_id, user_id, Number(selectedRoleLevel))
        } catch (error) {
            console.error("Error during changeEmployee call:", error);
            Toast.show({
                type: "error",
                text1: t("change_employee_toast_error"),
                text2: t("change_employee_toast_error_description"),
            });
        }
    }

    // Set header options based on fetched data
    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
            headerRight: () => {
                if (
                    hasPermission("club_delete_employees") &&
                    user &&
                    employee &&
                    employee.id !== user.id &&
                    employee.role_level !== 0
                ) {
                    return (
                        <Pressable onPress={handleDeletePress}>
                            <Icon
                                name="delete"
                                size={30}
                                color={iconColor}
                                style={{ marginLeft: "auto", marginRight: 15 }}
                            />
                        </Pressable>
                    );
                }
                return null;
            },
        });
    }, [navigation, iconColor, user, employee, hasPermission]);

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("manage_employee_heading")} />
                        </View>
                        <Subheading text={t("employee_info_subheading")} />
                        <DefaultTextFieldInput value={employee?.first_name} editable={false} />
                        <DefaultTextFieldInput value={employee?.last_name} editable={false} />
                        <DefaultTextFieldInput value={employee?.email} editable={false} />
                        {employee?.role_level !== 0 && (
                            <>
                                <Subheading text={t("employee_role_level_subheading")} />
                                <Dropdown
                                    values={roleOptions}
                                    setSelected={setSelectedRoleLevel}
                                    save="key"
                                    defaultOption={{
                                        key: employee?.role_level?.toString() || "",
                                        value: employee?.role_name || "",
                                    }}
                                />
                                <DefaultButton text={t("employee_change_role_btn")} onPress={handleRoleChangePress} />
                            </>
                        )}
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageEmployee;