import React, { useState } from "react";
import Heading from "@/src/components/textFields/Heading";
import { View, Platform, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback } from "react-native";
import { useRouter } from 'expo-router';
import { useTranslation } from "react-i18next";
import DefaultText from "@/src/components/textFields/DefaultText";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Subheading from "@/src/components/textFields/Subheading";
import TwoFactorInput from "@/src/components/textInputs/TwoFactorInput";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { totpRemove } from "@/src/services/user/totpService";

const SettingsDeactivateMFA = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    const [code, setCode] = useState("");
    const [codeError, setCodeError] = useState(true);
    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState(false);

    const handleMFADeactivatePress = async () => {
        if (codeError || passwordError) {
            if (!password.trim()) {
                setPasswordError(true);
            }
            Toast.show({
                type: 'error',
                text1: t("mfa_deactivate_error_empty"),
                text2: t("mfa_deactivate_error_subheading_empty"),
            });
            return;
        }

        try {
            await totpRemove(code, password);
            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/(tabs)/overview")
        } catch (error) {
            console.error("Error deactivating TOTP:", error);
            Toast.show({
                type: 'error',
                text1: t("mfa_deactivate_error"),
                text2: t("mfa_deactivate_error_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="py-4">
                        <Heading text={t("settings_deactivate_mfa_heading")} />
                    </View>
                    <Subheading text={t("settings_deactivate_mfa_description")} />
                    <TwoFactorInput
                        onCodeChange={(text, isComplete) => {
                            setCode(text);
                            if (isComplete) {
                                setCodeError(false);
                            } else {
                                setCodeError(true);
                            }
                        }}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("mfa_deactivate_password_textfield")}
                        value={password}
                        onChangeText={(text) => {
                            setPassword(text);
                            if (text.trim()) {
                                setPasswordError(false);
                            }
                        }}
                        secureTextEntry
                        hasError={passwordError}
                    />
                    <View className="py-4 w-full justify-center items-center">
                        <DefaultButton text={t("settings_deactivate_mfa_next")} onPress={handleMFADeactivatePress} />
                    </View>
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>

    );
};

export default SettingsDeactivateMFA;