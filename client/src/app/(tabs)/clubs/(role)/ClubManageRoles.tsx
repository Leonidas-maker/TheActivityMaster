import React, { useState, useEffect, useCallback } from "react";
import { ScrollView, View, useColorScheme, Pressable, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback, Platform } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams, useFocusEffect } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getClubPermissions } from "@/src/services/club/roleService";
import { getClubRoles } from "@/src/services/club/roleService";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

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

const ClubManageRoles = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const navigation = useNavigation();
    const { club_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    const [roles, setRoles] = useState<Role[]>([]);

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(role)/AddRole?club_id=${club_id}`);
    };

    useEffect(() => {
        navigation.setOptions({
            headerRight: () =>
                hasPermission("club_create_roles") ? (
                    <Pressable onPress={handleAddPress}>
                        <Icon
                            name="add"
                            size={30}
                            color={iconColor}
                            style={{ marginLeft: "auto", marginRight: 15 }}
                        />
                    </Pressable>
                ) : null,
        });
    }, [navigation, iconColor, hasPermission]);

    useFocusEffect(
        useCallback(() => {
            const fetchRoles = async () => {
                try {
                    const rolesData = await getClubRoles(club_id);
                    const filteredRoles = rolesData.filter((role: Role) => role.level !== 0);
                    setRoles(filteredRoles);
                } catch (error) {
                    console.error("Error during fetchRoles call:", error);
                }
            };
            fetchRoles();
        }, [club_id]));

    const texts = roles.map((role) => role.name);
    // Create onPress functions for each role with permission check
    const onPressFunctions = roles.map((role) => () => {
        // Check for permission "club_update_roles"
        if (!hasPermission("club_update_roles")) {
            // Show Toast message if permission is missing
            Toast.show({
                type: "info",
                text1: t("permissionError"),
                text2: t("permissionErrorDescription"),
            });
        } else {
            // Navigate to ManageRole screen if permission exists
            router.push(`/(tabs)/clubs/(role)/ManageRole?club_id=${club_id}&role_id=${role.id}`);
        }
    });
    const iconNames = roles.map(() => "person-search");

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <PageNavigator
                        title={t("manageRoles_navigator_title")}
                        texts={texts}
                        onPressFunctions={onPressFunctions}
                        iconNames={iconNames}
                    />
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ClubManageRoles;