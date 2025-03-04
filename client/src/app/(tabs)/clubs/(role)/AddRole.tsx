import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Pressable, Keyboard, KeyboardAvoidingView, Platform, TouchableWithoutFeedback } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Dropdown from "@/src/components/dropdown/Dropdown";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getClubPermissions, getClubRoles } from "@/src/services/club/roleService";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Subheading from "@/src/components/textFields/Subheading";
import { createClubRole } from "@/src/services/club/roleService";

const AddRole = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();

    const [roleName, setRoleName] = useState("");
    const [roleDescription, setRoleDescription] = useState("");
    const [roleNameError, setRoleNameError] = useState(false);
    const [roleDescriptionError, setRoleDescriptionError] = useState(false);

    // State to track the color scheme
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // State to store permissions data in dropdown format
    const [permissionsData, setPermissionsData] = useState<Array<{ key: string; value: string }>>([]);
    // State to store selected permission names
    const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

    // State for the available role levels after filtering out those already taken
    const [availableLevels, setAvailableLevels] = useState<Array<{ key: string; value: string }>>([]);
    // State for the selected role level
    const [selectedRoleLevel, setSelectedRoleLevel] = useState<string>("");

    const handleCreateRolePress = async () => {
        if (!roleName.trim()) {
            setRoleNameError(true);
        };

        if (!roleDescription.trim()) {
            setRoleDescriptionError(true);
        };

        if (!roleName.trim() || !roleDescription.trim() || !selectedRoleLevel || selectedPermissions.length === 0) {
            Toast.show({
                type: "error",
                text1: t("roleCreationErrorEmpty"),
                text2: t("roleCreationErrorEmptyDescription"),
            });
            return;
        };

        const role = {
            level: parseInt(selectedRoleLevel),
            name: roleName,
            description: roleDescription,
            permissions: selectedPermissions,
        };
        try {
            await createClubRole(club_id, role);
            router.dismiss();
        } catch (error) {
            console.error("Error creating role:", error);
            Toast.show({
                type: "error",
                text1: t("roleCreationError"),
                text2: t("roleCreationErrorDescription"),
            });
        }
    };

    // Fetch club permissions and set the dropdown data for permissions
    useEffect(() => {
        const fetchPermissions = async () => {
            try {
                const permissions = await getClubPermissions();
                // Map the response to an array of { key, value } objects
                const dropdownData = permissions.map((permission: { name: string; description: string }) => ({
                    key: permission.name,
                    value: permission.name,
                }));
                setPermissionsData(dropdownData);
            } catch (error) {
                console.error("Error fetching club permissions:", error);
            }
        };
        fetchPermissions();
    }, []);

    // Fetch club roles, then filter out the role levels that are already in use
    useEffect(() => {
        const fetchRoles = async () => {
            try {
                const roles = await getClubRoles(club_id);
                // Get an array of levels that are already taken
                const takenLevels = roles.map((role: { level: number }) => role.level);
                // Create an array with all possible levels from 0 to 10
                const allLevels = Array.from({ length: 11 }, (_, i) => i);
                // Filter out the levels that are already taken
                const filteredLevels = allLevels.filter((level) => !takenLevels.includes(level));
                // Map them to the format expected by the Dropdown component
                const dropdownLevels = filteredLevels.map((level) => ({
                    key: level.toString(),
                    value: level.toString(),
                }));
                setAvailableLevels(dropdownLevels);
            } catch (error) {
                console.error("Error fetching club roles:", error);
            }
        };
        fetchRoles();
    }, [club_id]);

    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleInfoPress = () => {
        router.navigate("/(tabs)/clubs/(role)/InfoRole");
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
                            <Heading text={t("create_role_heading")} />
                        </View>
                        <DefaultTextFieldInput
                            placeholder={t("role_name_placeholder")}
                            value={roleName}
                            onChangeText={(text) => {
                                setRoleName(text);
                                if (text.trim()) {
                                    setRoleNameError(false);
                                }
                            }}
                            hasError={roleNameError}
                        />
                        <DefaultTextFieldInput
                            placeholder={t("role_description_placeholder")}
                            value={roleDescription}
                            onChangeText={(text) => {
                                setRoleDescription(text);
                                if (text.trim()) {
                                    setRoleDescriptionError(false);
                                }
                            }}
                            hasError={roleDescriptionError}
                        />
                        <Subheading text={t("role_level_subheading")} />
                        <Dropdown
                            setSelected={setSelectedRoleLevel}
                            values={availableLevels}
                            placeholder={t("selectRoleLevel_placeholder")}
                        />
                        <Subheading text={t("role_permissions_subheading")} />
                        <MultiDropdown
                            setSelected={setSelectedPermissions}
                            values={permissionsData}
                            placeholder={t("selectPermissions_placeholder")}
                            notFound={t("selectPermissions_notFound")}
                            searchPlaceholderText={t("selectPermissions_searchPlaceholder")}
                            useSections={false}
                            confirmButtonText={t("selectPermissions_confirmButton")}
                        />
                        <View className="w-full justify-center items-center pt-4">
                            <DefaultButton text={t("add_role_btn")} onPress={handleCreateRolePress} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddRole;
