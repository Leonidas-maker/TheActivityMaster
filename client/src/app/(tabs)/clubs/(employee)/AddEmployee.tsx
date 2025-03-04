import React, { useEffect, useState } from "react";
import { ScrollView, View, Pressable, useColorScheme, Alert, Platform, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import Dropdown from "@/src/components/dropdown/Dropdown";
import { getClubRoles } from "@/src/services/club/roleService";
import { addEmployee } from "@/src/services/club/employeeService";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";

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

const AddEmployee = () => {
    const { t } = useTranslation("clubs");
    const router = useRouter();
    const navigation = useNavigation();
    const { club_id } = useLocalSearchParams();

    const [userIdent, setUserIdent] = useState("");
    const [userIdentError, setUserIdentError] = useState(false);
    const [selectedRoleError, setSelectedRoleError] = useState(false);

    // State to store formatted roles for the dropdown (each object has key: role level, and value: role name)
    const [roleOptions, setRoleOptions] = useState<{ key: string; value: string }[]>([]);
    // State to store the selected role level
    const [selectedRoleLevel, setSelectedRoleLevel] = useState("");

    useEffect(() => {
        const fetchRoles = async () => {
            try {
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
                console.error("Error during fetchRoles call:", error);
            }
        };
        fetchRoles();
    }, [club_id]);

    const handleAddEmployeePress = async () => {
        if (!userIdent.trim()) {
            setUserIdentError(true);
        }

        if (!selectedRoleLevel) {
            setSelectedRoleError(true);
        }

        if (!userIdent.trim() || !selectedRoleLevel) {
            Toast.show({
                type: "error",
                text1: t("add_employee_empty_toast_error"),
                text2: t("add_employee_empty_toast_error_description"),
            });
            return;
        }

        try {
            await addEmployee(club_id, userIdent, Number(selectedRoleLevel));
            router.dismiss();
        } catch (error) {
            console.error("Error during addEmployee call:", error);
            Toast.show({
                type: "error",
                text1: t("add_employee_toast_error"),
                text2: t("add_employee_toast_error_description"),
            });
        }
    };

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleInfoPress = () => {
        Alert.alert(t("add_employee_alert_title"), t("add_employee_alert_text"));
    };

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
            headerRight: () => (
                <Pressable onPress={handleInfoPress}>
                    <Icon
                        name="info"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("add_employee_heading")} />
                        </View>
                        <DefaultTextFieldInput
                            placeholder={t("user_ident_placeholder")}
                            value={userIdent}
                            onChangeText={(text) => {
                                setUserIdent(text);
                                if (text.trim()) {
                                    setUserIdentError(false);
                                }
                            }}
                            hasError={userIdentError}
                        />
                        <Dropdown
                            values={roleOptions}
                            setSelected={setSelectedRoleLevel}
                            placeholder={t("add_employee_role_placeholder")}
                            save="key"
                        />
                        <DefaultButton text={t("add_employee_button")} onPress={handleAddEmployeePress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddEmployee;
