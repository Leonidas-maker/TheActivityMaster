import React, { useEffect, useState } from "react";
import { ScrollView, View, Text, Pressable, useColorScheme } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation } from "expo-router";
import { getClubPermissions } from "@/src/services/club/roleService";
import Subheading from "@/src/components/textFields/Subheading";
import Icon from "react-native-vector-icons/MaterialIcons";

interface Permission {
    name: string;
    description: string;
}

const InfoRole = () => {
    // Router and translation hooks
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");

    // State for storing permissions
    const [permissions, setPermissions] = useState<Permission[]>([]);

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
        });
    }, [navigation, iconColor]);

    // Fetch permissions when component mounts
    useEffect(() => {
        const fetchPermissions = async () => {
            try {
                const fetchedPermissions = await getClubPermissions();
                setPermissions(fetchedPermissions);
            } catch (error) {
                console.error("Error fetching permissions:", error);
            }
        }
        fetchPermissions();
    }, []);

    return (
        <ScrollView className="flex-1 bg-light_primary dark:bg-dark_primary">
            {/* Container for header and list */}
            <View className="px-4 py-6">
                <Heading text={t("club_role_permissions_heading")} />
                <Subheading text={t("club_role_permission_subheading")} />

                {/* List container with spacing between cards */}
                <View className="mt-4 space-y-4">
                    {permissions.map((permission) => (
                        <View
                            key={permission.name}
                            className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-md"
                        >
                            {/* Permission name */}
                            <Text
                                className="text-lg font-semibold text-gray-800 dark:text-gray-100"
                            >{permission.name}</Text>
                            {/* Permission description */}
                            <Text
                                className="mt-1 text-gray-600 dark:text-gray-300"
                            >{permission.description}</Text>
                        </View>
                    ))}
                </View>
            </View>
        </ScrollView>
    );
}

export default InfoRole;
