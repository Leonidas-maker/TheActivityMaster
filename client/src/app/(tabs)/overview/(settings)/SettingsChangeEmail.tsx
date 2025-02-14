import React, { useState } from "react";
import { View, KeyboardAvoidingView, Platform, Keyboard, TouchableWithoutFeedback } from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { changeEmail } from "@/src/services/user/userService";


const SettingsChangeEmail = () => {
    // Initialize state for the text fields
    const [password, setPassword] = useState("");
    const [newEmail, setNewEmail] = useState("");
    const [confirmEmail, setConfirmEmail] = useState("");
    const [passwordError, setPasswordError] = useState(false);
    const [newEmailError, setNewEmailError] = useState(false);
    const [confirmEmailError, setConfirmEmailError] = useState(false);

    const router = useRouter();
    const { t } = useTranslation("settings");

    // Helper function to check if an email is valid.
    const isValidEmail = (email: string): boolean => {
        const emailRegex = /^\S+@\S+\.\S+$/;
        return emailRegex.test(email);
    };

    const handleEmailChangePress = async () => {
        if (!password.trim() || !newEmail.trim() || !confirmEmail.trim()) {
            if (!password.trim()) {
                setPasswordError(true);
            }
            if (!newEmail.trim()) {
                setNewEmailError(true);
            }
            if (!confirmEmail.trim()) {
                setConfirmEmailError(true);
            }
            Toast.show({
                type: "error",
                text1: t("error_change_email_all_fields"),
                text2: t("error_fill_all_fields_email_subheading"),
            });
            return;
        };

        // Check if the provided emails are valid.
        if (!isValidEmail(newEmail) || !isValidEmail(confirmEmail)) {
            setNewEmailError(true);
            setConfirmEmailError(true);
            Toast.show({
                type: "error",
                text1: t("emailInvalidError_text"),
                text2: t("emailInvalidError_subtext"),
            });
            return;
        }

        if (newEmail !== confirmEmail) {
            setConfirmEmailError(true);
            setNewEmailError(true);
            Toast.show({
                type: "error",
                text1: t("error_email_mismatch"),
                text2: t("error_email_mismatch_subheading"),
            });
            return;
        }

        try {
            // Pass the state values to the service
            await changeEmail(newEmail, password);

            router.navigate("/(tabs)/overview/(settings)/SettingsChangeEmailInfo");
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("error_change_email_failed"),
                text2: t("error_change_email_failed_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("change_email_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("change_email_new_placeholder")}
                        value={newEmail}
                        onChangeText={(text) => {
                            setNewEmail(text);
                            if (text.trim()) {
                                setNewEmailError(false);
                            }
                        }}
                        hasError={newEmailError}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("change_email_confirm_placeholder")}
                        value={confirmEmail}
                        onChangeText={(text) => {
                            setConfirmEmail(text);
                            if (text.trim()) {
                                setConfirmEmailError(false);
                            }
                        }}
                        hasError={confirmEmailError}
                    />
                    <DefaultTextFieldInput
                        secureTextEntry={true}
                        placeholder={t("change_email_password_placeholder")}
                        value={password}
                        onChangeText={(text) => {
                            setPassword(text);
                            if (text.trim()) {
                                setPasswordError(false);
                            }
                        }}
                        hasError={passwordError}
                    />
                    <DefaultButton text={t("change_email_button")} onPress={handleEmailChangePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsChangeEmail;