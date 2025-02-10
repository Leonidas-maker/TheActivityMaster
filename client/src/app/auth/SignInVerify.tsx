import React, { useEffect, useState } from "react";
import { View, KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { useTranslation } from "react-i18next";
import { verify2fa } from "@/src/services/auth/loginService";
import { useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { secureSaveData } from "@/src/services/secureStorageService";
import Heading from "@/src/components/textFields/Heading";
import TwoFactorInput from "@/src/components/textInputs/TwoFactorInput";
import { useRouter } from "expo-router";

const SignInVerify: React.FC = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();
    const [code, setCode] = useState("");
    const [error, setError] = useState(true);
    const [isEmail, setIsEmail] = useState(false);

    const { securityToken, methods } = useLocalSearchParams();

    useEffect(() => {
        if (methods.includes("email")) {
            setIsEmail(true);
        }
    }, []);

    // Handle the verification button press event
    const handleVerifyPress = async () => {
        if (error) {
            Toast.show({
                type: "error",
                text1: t("toastErrorSignInVerify_emptyText"),
                text2: t("toastErrorSignInVerify_emptySubtext"),
            });
            return;
        }

        const token = Array.isArray(securityToken) ? securityToken[0] : securityToken;
        const method = Array.isArray(methods) ? methods[0] : methods;

        try {
            const response = await verify2fa(token, code, [method]);
            const { access_token, refresh_token } = response;

            // Save the tokens to secure storage
            await secureSaveData("access_token", access_token + "fake");
            await secureSaveData("refresh_token", refresh_token);

            router.navigate("/(tabs)");
        } catch (error: any) {
            console.error("2FA error:", error);
            Toast.show({
                type: "error",
                text1: t("toastErrorSignInVerify_errorText"),
                text2: t("toastErrorSignInVerify_errorSubtext"),
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
                        <Heading text={isEmail ? t("signInVerifyMail_text") : t("signInVerifyApp_text")} />
                    </View>
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
                    <DefaultButton text={t("signInVerify_btn")} onPress={handleVerifyPress} />
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default SignInVerify;
