import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Alert, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import { deleteProgram } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";

const ManageProgram = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, program_id } = useLocalSearchParams();

    // States for color scheme
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
        Alert.alert(t("programDeletionAlertTitle"), t("programDeletionAlertDescription"), [
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
            await deleteProgram(club_id, program_id);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    }

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
                <Pressable onPress={handleDeletePress}>
                    <Icon
                        name="delete"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            )
        });
    }, [navigation, iconColor]);

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="items-center">
                <Heading text={t("createClub")} />
                <DefaultTextFieldInput placeholder={t("clubName")} />
                <DefaultTextFieldInput placeholder={t("clubDescription")} />
                <DefaultButton text={t("create")} />
            </View>
            <DefaultToast />
        </ScrollView>
    );
}

export default ManageProgram;