import React, { useEffect, useState } from "react";
import { ScrollView, View, useColorScheme, Pressable, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback, Platform } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import { deleteMembership } from "@/src/services/club/membershipService";
import Subheading from "@/src/components/textFields/Subheading";

const DeleteMembership = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, membership_id } = useLocalSearchParams();

    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState(false);
    const handleDeleteMembershipPress = async () => {
        if (!password.trim()) {
            setPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext")
            });
            return;
        }
        try {
            await deleteMembership(club_id, membership_id, password);
            for (let i = 0; i < 2; i++) {
                router.back();
            }
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    // Color scheme state
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
            )
        });
    }, [navigation, iconColor]);

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="pt-4">
                            <Heading text={t("delete_membership_heading")} />
                        </View>
                        <Subheading text={t("delete_membership_subheading")} />
                        <DefaultTextFieldInput
                            placeholder={t("password_placeholder")}
                            secureTextEntry
                            value={password}
                            onChangeText={(text) => {
                                setPassword(text);
                                if (text.trim()) {
                                    setPasswordError(false);
                                }
                            }}
                            hasError={passwordError}
                        />
                        <DefaultButton text={t("delete_membership_btn")} onPress={handleDeleteMembershipPress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
}

export default DeleteMembership;