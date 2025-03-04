import React, { useEffect, useState } from "react";
import { ScrollView, View, Pressable, useColorScheme, TouchableWithoutFeedback, Keyboard, Platform, KeyboardAvoidingView } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getClubRoleMembers, getClubRole, deleteClubRole, updateClubRole } from "@/src/services/club/roleService";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";

const ManageRole = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, role_id } = useLocalSearchParams();

    // State to track the color scheme
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleDeletePress = async () => {
        try {
            await deleteClubRole(club_id, role_id);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleDeletionError"),
                text2: t("roleDeletionErrorDescription"),
            });
        }
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
                <Pressable onPress={handleDeletePress}>
                    <Icon
                        name="delete"
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
                        <Heading text={t("createClub")} />
                        <DefaultTextFieldInput placeholder={t("clubName")} />
                        <DefaultTextFieldInput placeholder={t("clubDescription")} />
                        <DefaultButton text={t("create")} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
}

export default ManageRole;