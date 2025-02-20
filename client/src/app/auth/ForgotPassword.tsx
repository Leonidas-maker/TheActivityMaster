import React, { useState } from "react";
import { View, TouchableWithoutFeedback, KeyboardAvoidingView, Platform, Keyboard } from 'react-native';
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { forgotPassword } from "@/src/services/auth/forgotService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

const ForgotPassword = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    const [ident, setIdent] = useState("");
    const [identError, setIdentError] = useState(false);

    const handleForgotPress = async () => {
        if (!ident.trim()) {
            setIdentError(true);
            Toast.show({
                type: "error",
                text1: t("forgot_password_error_empty"),
                text2: t("forgot_password_error_empty_subtext"),
            });
            return;
        }

        try {
            await forgotPassword(ident);

            router.navigate("/auth/(info)/VerifyPasswordReset");
        } catch (error) {
            console.error("Forgot password error:", error);
            Toast.show({
                type: "error",
                text1: t("forgot_password_error"),
                text2: t("forgot_password_error_subtext"),
            });
            return;
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
                        <Heading text={t("forgot_password_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("forgot_password_ident_placeholder")}
                        value={ident}
                        onChangeText={(text) => {
                            setIdent(text);
                            if (text.trim()) {
                                setIdentError(false);
                            }
                        }}
                        hasError={identError}
                    />
                    <DefaultButton text={t("forgot_password_button")} onPress={handleForgotPress} />
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ForgotPassword;