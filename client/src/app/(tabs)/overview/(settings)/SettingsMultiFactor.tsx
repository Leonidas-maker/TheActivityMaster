import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import TwoFactorInput from "@/src/components/textInputs/TwoFactorInput";
import React, { useState, useRef } from "react";
import { ScrollView, View, TouchableWithoutFeedback, Platform, Keyboard, KeyboardAvoidingView, Text } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { totpRegister } from "@/src/services/user/totpService";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import * as Clipboard from 'expo-clipboard';
import Subheading from "@/src/components/textFields/Subheading";
import type { ConfettiMethods } from 'react-native-fast-confetti';
import { Confetti } from "react-native-fast-confetti";

const SettingsMultiFactor = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    const [code, setCode] = useState("");
    const [error, setError] = useState(true);
    const [disabled, setDisabled] = useState(false);
    const [step, setSteps] = useState(0);
    const [backupCodes, setBackupCodes] = useState<string[]>([]);

    // Async handler to enable multi-factor authentication
    const handleEnablePress = async () => {
        // If the code is incomplete, show an error toast
        if (error) {
            Toast.show({
                type: 'error',
                text1: t("mfa_enabled_error_empty"),
                text2: t("mfa_enabled_error_subheading_empty"),
            });
            return;
        }

        // Disable the button to prevent multiple requests
        setDisabled(true);

        try {
            // Wait for the async registration to complete
            await totpRegister(code).then((response) => {
                // Set the backup codes and move to the success step
                setBackupCodes(response.backup_codes);
                setSteps(1);
            });

            setSteps(1);
            confettiRef.current?.restart();
        } catch (error) {
            console.error("Error enabling TOTP:", error);
            // Show an error toast if the request fails
            Toast.show({
                type: 'error',
                text1: t("mfa_enabled_error"),
                text2: t("mfa_enabled_error_subheading"),
            });
        } finally {
            // Always re-enable the button after the async call
            setDisabled(false);
        }
    };

    const handleBackPress = () => {
        // Navigate back until there are no more routes to pop
        while (router.canGoBack()) {
            router.back();
        }
        router.navigate("/(tabs)/overview");
    };

    const handleCopyPress = async () => {
        await Clipboard.setStringAsync(backupCodes.join(", "));

        Toast.show({
            type: "success",
            text1: t("settings_enable_mfa_secret_copied"),
        });
    };

    // Create a ref to control the confetti component
    const confettiRef = useRef<ConfettiMethods>(null);

    // Helper function to render backup codes in a table (2 columns x 4 rows)
    const renderBackupCodesTable = () => {
        // Create an array of rows; each row contains 2 codes.
        const rows = [];
        for (let i = 0; i < 4; i++) {
            const leftCode = backupCodes[i * 2] || "";
            const rightCode = backupCodes[i * 2 + 1] || "";
            rows.push(
                <View key={i} className="flex-row justify-between w-full my-2">
                    <View className="flex-1 border p-2 m-1 items-center dark:border-white">
                        <DefaultText text={leftCode} />
                    </View>
                    <View className="flex-1 border p-2 m-1 items-center dark:border-white">
                        <DefaultText text={rightCode} />
                    </View>
                </View>
            );
        }
        return <View className="w-full px-4">{rows}</View>;
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    {step === 0 && (
                        <>
                            <Heading text={t("multi_factor_authentication_enable_title")} />
                            <View className="py-4">
                                <TwoFactorInput
                                    onCodeChange={(text, isComplete) => {
                                        setCode(text);
                                        setError(!isComplete);
                                    }}
                                />
                            </View>
                            <DefaultButton text={t("mfa_enable_button")} onPress={handleEnablePress} disabled={disabled} />
                        </>
                    )}
                    {step === 1 && (
                        <>
                            <View className="py-4">
                                <Heading text={t("multi_factor_authentication_enable_success_title")} />
                            </View>
                            <Subheading text={t("mfa_enable_success_subheading")} />
                            {renderBackupCodesTable()}
                            <SecondaryButton text={t("mfa_enable_copy_secondary_button")} onPress={handleCopyPress} />
                            <DefaultButton text={t("mfa_enable_success_button")} onPress={handleBackPress} />
                        </>
                    )}
                </View>
            </TouchableWithoutFeedback>
            <Confetti ref={confettiRef} isInfinite={false} autoplay={false} />
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default SettingsMultiFactor;
