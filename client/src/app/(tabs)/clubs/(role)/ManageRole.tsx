import React, { useEffect, useState } from "react";
import {
    ScrollView,
    View,
    Pressable,
    useColorScheme,
    TouchableWithoutFeedback,
    Keyboard,
    Platform,
    KeyboardAvoidingView,
    Alert
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import {
    getClubRoleMembers,
    getClubRole,
    deleteClubRole,
    updateClubRole,
    getClubRoles,
    getClubPermissions
} from "@/src/services/club/roleService";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Dropdown from "@/src/components/dropdown/Dropdown";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import Subheading from "@/src/components/textFields/Subheading";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

const ManageRole = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, role_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    // States for text fields
    const [roleName, setRoleName] = useState("");
    const [roleDescription, setRoleDescription] = useState("");
    const [roleNameError, setRoleNameError] = useState(false);
    const [roleDescriptionError, setRoleDescriptionError] = useState(false);

    const [initialRoleName, setInitialRoleName] = useState("");
    const [initialRoleDescription, setInitialRoleDescription] = useState("");
    const [initialRoleLevel, setInitialRoleLevel] = useState("");
    const [initialRolePermissions, setInitialRolePermissions] = useState([]);

    // States for color scheme
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // States for role levels dropdown
    const [availableRoleLevels, setAvailableRoleLevels] = useState<
        { key: string; value: string }[]
    >([]);
    const [selectedRoleLevel, setSelectedRoleLevel] = useState<{
        key: string;
        value: string;
    }>({ key: "", value: "" });

    // States for permissions multi-dropdown
    const [availablePermissions, setAvailablePermissions] = useState<
        { key: string; value: string }[]
    >([]);
    const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

    // State for role members to pass to PageNavigator
    const [roleMembers, setRoleMembers] = useState<
        { first_name: string; last_name: string; email: string; id: string }[]
    >([]);

    // Helper function to compare two arrays irrespective of order
    const arraysEqual = (a: string[], b: string[]) => {
        if (a.length !== b.length) return false;
        const sortedA = [...a].sort();
        const sortedB = [...b].sort();
        return sortedA.every((val, index) => val === sortedB[index]);
    };

    // Handler functions
    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleDeletePress = async () => {
        Alert.alert(t("roleDeletionAlertTitle"), t("roleDeletionAlertDescription"), [
            {
                text: t("cancel_btn"),
                style: "cancel"
            },
            {
                text: t("confirm_btn"),
                onPress: handleDeleteConfirm
            }
        ]);
    };

    const handleDeleteConfirm = async () => {
        try {
            await deleteClubRole(club_id, role_id);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    const handleUpdatePress = async () => {
        if (!roleName.trim()) {
            setRoleNameError(true);
        }
        if (!roleDescription.trim()) {
            setRoleDescriptionError(true);
        }
        if (!roleName.trim() || !roleDescription.trim()) {
            Toast.show({
                type: "error",
                text1: t("roleManageEmptyError"),
                text2: t("roleManageEmptyErrorDescription")
            });
            return;
        }
        if (
            roleName === initialRoleName &&
            roleDescription === initialRoleDescription &&
            selectedRoleLevel.value === initialRoleLevel &&
            arraysEqual(selectedPermissions, initialRolePermissions)
        ) {
            Toast.show({
                type: "info",
                text1: t("roleManageInfo"),
                text2: t("roleManageInfoDescription")
            });
            return;
        }

        const updatedRole = {
            name: roleName,
            description: roleDescription,
            level: parseInt(selectedRoleLevel.value),
            permissions: selectedPermissions
        };
        try {
            await updateClubRole(club_id, role_id, updatedRole);

            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    // Fetch current role
    useEffect(() => {
        const fetchRole = async () => {
            try {
                const role = await getClubRole(club_id, role_id);
                setRoleName(role.name);
                setRoleDescription(role.description);
                setInitialRoleName(role.name);
                setInitialRoleDescription(role.description);
                setInitialRoleLevel(role.level.toString());
                setInitialRolePermissions(role.permissions.map((p: any) => p.name));
                setSelectedRoleLevel({
                    key: role.level.toString(),
                    value: role.level.toString()
                });
                setSelectedPermissions(role.permissions.map((p: any) => p.name));
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchRole();
    }, [club_id, role_id]);

    // Fetch all available roles for the dropdown and merge the current role level if needed
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
                let dropdownLevels = filteredLevels.map((level) => ({
                    key: level.toString(),
                    value: level.toString(),
                }));
                // Add the current role's level if it is not already included and is not the default empty value
                if (
                    selectedRoleLevel.value &&
                    !dropdownLevels.some((item) => item.value === selectedRoleLevel.value)
                ) {
                    dropdownLevels.push(selectedRoleLevel);
                    // Sort levels numerically based on their value
                    dropdownLevels.sort(
                        (a, b) => parseInt(a.value) - parseInt(b.value)
                    );
                }
                setAvailableRoleLevels(dropdownLevels);
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchRoles();
    }, [club_id, selectedRoleLevel]);

    // Fetch available permissions for the multi-dropdown
    useEffect(() => {
        const fetchPermissions = async () => {
            try {
                const perms = await getClubPermissions();
                const permsValues = perms.map((p: any) => ({
                    key: p.name,
                    value: p.name
                }));
                setAvailablePermissions(permsValues);
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchPermissions();
    }, []);

    // Fetch role members for the page navigator
    useEffect(() => {
        const fetchRoleMembers = async () => {
            try {
                const members = await getClubRoleMembers(club_id, role_id);
                setRoleMembers(members);
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchRoleMembers();
    }, [club_id, role_id]);

    // Set navigation header buttons
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
                hasPermission("club_delete_roles") ? (
                <Pressable onPress={handleDeletePress}>
                    <Icon
                        name="delete"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
                ) : null
            )
        });
    }, [navigation, iconColor]);

    // Build PageNavigator props for role members
    const memberNames = roleMembers.map(
        (member) => `${member.first_name} ${member.last_name}`
    );
    const memberOnPressFunctions = roleMembers.map((member) => () =>
        router.push(
            `/(tabs)/clubs/(employee)/ManageEmployee?user_id=${member.id}&club_id=${club_id}`
        )
    );
    const memberIconNames = roleMembers.map(() => "person");

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("edit_role_heading")} />
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
                            setSelected={(selectedValue: string) =>
                                setSelectedRoleLevel({ key: selectedValue, value: selectedValue })
                            }
                            values={availableRoleLevels}
                            placeholder={t("select_role_level")}
                            defaultOption={selectedRoleLevel}
                        />
                        <Subheading text={t("role_permissions_subheading")} />
                        <MultiDropdown
                            selectedItems={selectedPermissions}
                            initialSelected={selectedPermissions}
                            setSelected={setSelectedPermissions}
                            values={availablePermissions}
                            placeholder={t("selectPermissions_placeholder")}
                            useSections={false}
                        />
                        <View className="w-full justify-center items-center pt-4">
                            <DefaultButton text={t("edit_role_btn")} onPress={handleUpdatePress} />
                        </View>
                        {roleMembers.length > 0 &&
                            <>
                                <Subheading text={t("role_members_subheading")} />
                                <View className="w-full pb-10">
                                    <PageNavigator
                                        title={t("role_members_subheading")}
                                        texts={memberNames}
                                        onPressFunctions={memberOnPressFunctions}
                                        iconNames={memberIconNames}
                                    />
                                </View>
                            </>
                        }
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageRole;
