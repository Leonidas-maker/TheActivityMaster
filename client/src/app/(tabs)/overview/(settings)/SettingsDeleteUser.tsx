import React, { useState } from "react";
import { View, KeyboardAvoidingView, TouchableWithoutFeedback, Platform, Keyboard } from "react-native";
import { useTranslation } from "react-i18next";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Heading from "@/src/components/textFields/Heading";
import { useRouter } from "expo-router";
import Toast from "react-native-toast-message";
import { deleteUser } from "@/src/services/user/userService";
import { secureRemoveData } from "@/src/services/secureStorageService";
import { asyncRemoveData } from "@/src/services/asyncStorageService";

const SettingsDeleteUser = () => {
    const router = useRouter();
    const { t } = useTranslation("settings");
    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState(false);

    const handleDeleteUserPress = async () => {
        if (!password.trim()) {
            setPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("error_delete_all_fields"),
                text2: t("error_fill_all_fields_delete_subheading"),
            });
            return;
        }

        try {
            await deleteUser(password);
            // Use Promise.all to wait for all removal operations to complete
            await Promise.all([
                secureRemoveData("access_token"),
                secureRemoveData("refresh_token"),
                asyncRemoveData("savedUsername"),
                secureRemoveData("savedPassword"),
                asyncRemoveData("isLoggedIn"),
                asyncRemoveData("wasLoggedIn"),
                asyncRemoveData("isVerified")
            ]);
            // Clear the router history and navigate to the tabs screen
            // Its a bit pfuschy but it works (expo-router discussion #495)
            while (router.canGoBack()) {
                router.back();
            }
            router.push("/(tabs)");
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("error_delete_user_failed"),
                text2: t("error_delete_user_failed_subheading"),
            });
        }
    }

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("delete_user_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        secureTextEntry={true}
                        placeholder={t("delete_password_placeholder")}
                        value={password}
                        onChangeText={(text) => {
                            setPassword(text);
                            if (text.trim()) {
                                setPasswordError(false);
                            }
                        }}
                        hasError={passwordError}
                    />
                    <DefaultButton text={t("delete_user_button")} onPress={handleDeleteUserPress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsDeleteUser;