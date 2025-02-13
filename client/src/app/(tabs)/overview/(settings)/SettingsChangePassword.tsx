import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { changePassword } from "@/src/services/user/userService";
import React, { useState } from "react";
import { View, TouchableWithoutFeedback, Keyboard, KeyboardAvoidingView, Platform } from "react-native";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

const SettingsChangePassword = () => {
    // Initialize state for the text fields
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [oldPasswordError, setOldPasswordError] = useState(false);
    const [newPasswordError, setNewPasswordError] = useState(false);
    const [confirmNewPasswordError, setConfirmNewPasswordError] = useState(false);

    const router = useRouter();
    const { t } = useTranslation("settings");

    const handlePasswordChangePress = async () => {
        if (!oldPassword.trim() || !newPassword.trim() || !confirmNewPassword.trim()) {
            if (!oldPassword.trim()) {
                setOldPasswordError(true);
            }
            if (!newPassword.trim()) {
                setNewPasswordError(true);
            }
            if (!confirmNewPassword.trim()) {
                setConfirmNewPasswordError(true);
            }
            Toast.show({
                type: "error",
                text1: t("error"),
                text2: t("fill_all_fields"),
            });
            return;
        };

        // Ensure the new password and confirm password match
        if (newPassword !== confirmNewPassword) {
            setNewPasswordError(true);
            setConfirmNewPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("error"),
                text2: t("passwords_do_not_match"),
            });
            return;
        }

        if (newPassword.length < 8) {
            setNewPasswordError(true);
            setConfirmNewPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("error"),
                text2: t("password_too_short"),
            });
            return;
        }

        try {
            // Pass the state values to the service
            await changePassword(oldPassword, newPassword);

            router.back();
        } catch (error) {
            setOldPasswordError(true);
            Toast.show({
                type: "error",
                text1: "Error",
                text2: "Failed to change password",
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("change_password_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("change_password_old_placeholder")}
                        value={oldPassword}
                        onChangeText={(text) => {
                            setOldPassword(text);
                            if (text.trim()) {
                                setOldPasswordError(false);
                            }
                        }}
                        hasError={oldPasswordError}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("change_password_placeholder")}
                        value={newPassword}
                        onChangeText={(text) => {
                            setNewPassword(text);
                            if (text.trim()) {
                                setNewPasswordError(false);
                            }
                        }}
                        hasError={newPasswordError}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("change_password_confirm_placeholder")}
                        value={confirmNewPassword}
                        onChangeText={(text) => {
                            setConfirmNewPassword(text);
                            if (text.trim()) {
                                setConfirmNewPasswordError(false);
                            }
                        }}
                        hasError={confirmNewPasswordError}
                    />
                    <DefaultButton text={t("change_password_button")} onPress={handlePasswordChangePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsChangePassword;