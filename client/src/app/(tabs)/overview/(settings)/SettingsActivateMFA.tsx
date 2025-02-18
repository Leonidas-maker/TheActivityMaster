import Heading from "@/src/components/textFields/Heading";
import React, { useEffect, useState } from "react";
import { View } from "react-native";
import QRCode from "react-native-qrcode-svg";
import { useRouter, router } from 'expo-router';
import { useTranslation } from "react-i18next";
import { totpRegisterInit } from "@/src/services/user/totpService";
import DefaultText from "@/src/components/textFields/DefaultText";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import * as Clipboard from 'expo-clipboard';
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

const SettingsActivateMFA = () => {
    const { t } = useTranslation();
    const router = useRouter();

    const [uri, setUri] = useState("");
    const [secret, setSecret] = useState("");

    useEffect(() => {
        const initTotp = async () => {
            const response = await totpRegisterInit();
            setUri(response.uri);
            setSecret(response.secret);
        };
        initTotp();
    }, []);

    const handleCopySecretPress = async () => {
        await Clipboard.setStringAsync(secret);

        Toast.show({
            type: "success",
            text1: t("settings_activate_mfa_secret_copied"),
            visibilityTime: 3000,
        });
    };

    // If the uri is not yet available, show a loading message
    if (!uri) {
        return (
            <View className="flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary">
                <DefaultText text={t("loading")} />
            </View>
        );
    }

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <View className="py-4">
                <Heading text={t("settings_activate_mfa_heading")} />
            </View>
            <View className="pb-4">
                <QRCode
                    value={uri}
                    size={200}
                    backgroundColor="white"
                    color="black"
                    quietZone={10}
                />
            </View>
            <DefaultText text={t("settings_activate_mfa_cant_scan")} />
            <SecondaryButton text={t("settings_activate_mfa_manual")} onPress={handleCopySecretPress} />
            <DefaultToast />
        </View>
    );
};

export default SettingsActivateMFA;