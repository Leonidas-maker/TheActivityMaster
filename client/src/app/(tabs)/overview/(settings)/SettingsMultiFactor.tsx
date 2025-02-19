import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import TwoFactorInput from "@/src/components/textInputs/TwoFactorInput";
import React from "react";
import { ScrollView, View, TouchableWithoutFeedback, Platform, Keyboard, KeyboardAvoidingView } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { totpRegister } from "@/src/services/user/totpService";

const SettingsMultiFactor = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    const [code, setCode] = React.useState("");
    const [error, setError] = React.useState(true);

    const handleEnablePress = async () => {
        if (error) {
            Toast.show({
                type: 'error',
                text1: t("mfa_enabled_error_empty"),
                text2: t("mfa_enabled_error_subheading_empty"),
            });
            return;
        }

        try {
            await totpRegister(code);
            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/(tabs)/overview")
        } catch (error) {
            console.error("Error enabling TOTP:", error);
            Toast.show({
                type: 'error',
                text1: t("mfa_enabled_error"),
                text2: t("mfa_enabled_error_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <Heading text={t("multi_factor_authentication_enable_title")} />
                    <View className="py-4">
                        <TwoFactorInput
                            onCodeChange={(text, isComplete) => {
                                setCode(text);
                                if (isComplete) {
                                    setError(false);
                                } else {
                                    setError(true);
                                }
                            }}
                        />
                    </View>
                    <DefaultButton text={t("mfa_enable_button")} onPress={handleEnablePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsMultiFactor;