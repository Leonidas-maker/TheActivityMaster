import React, { useState } from "react";
import { View, TouchableWithoutFeedback, Platform, Keyboard, KeyboardAvoidingView } from "react-native";
import { useTranslation } from "react-i18next";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useRouter, useLocalSearchParams } from "expo-router";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { resetPassword } from "@/src/services/auth/forgotService";

const ResetPassword = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState(false);
    const [confirmPassword, setConfirmPassword] = useState("");
    const [confirmPasswordError, setConfirmPasswordError] = useState(false);

    const { security_token } = useLocalSearchParams();

    const handleResetPasswordPress = async () => {
        if (!password.trim() || !confirmPassword.trim()) {
            if (!password.trim()) setPasswordError(true);
            if (!confirmPassword.trim()) setConfirmPasswordError(true);

            Toast.show({
                type: "error",
                text1: t("reset_password_error"),
                text2: t("reset_password_error_message"),
            });
            return;
        }

        if (password !== confirmPassword) {
            setPasswordError(true);
            setConfirmPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("reset_password_invalid_error"),
                text2: t("reset_password_invalid_error_message"),
            });
            return;
        }

        if (password.length < 8) {
            setPasswordError(true);
            Toast.show({
                type: "error",
                text1: t("reset_password_length_error"),
                text2: t("reset_password_length_error_message"),
            });
            return;
        }

        try {
            await resetPassword(password, Array.isArray(security_token) ? security_token[0] : security_token);

            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/(tabs)");
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("reset_password_other_error"),
                text2: t("reset_password_other_error_generic"),
            });
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="py-4">
                        <Heading text={t("reset_password_heading")} />
                    </View>
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
                    <DefaultTextFieldInput
                        placeholder={t("confirm_password_placeholder")}
                        secureTextEntry
                        value={confirmPassword}
                        onChangeText={(text) => {
                            setConfirmPassword(text);
                            if (text.trim()) {
                                setConfirmPasswordError(false);
                            }
                        }}
                        hasError={confirmPasswordError}
                    />
                    <DefaultButton text={t("reset_password_reset_button")} onPress={handleResetPasswordPress} />
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ResetPassword;