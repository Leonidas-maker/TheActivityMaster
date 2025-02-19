import Heading from "@/src/components/textFields/Heading";
import React, { useEffect, useState } from "react";
import { View } from "react-native";
import { useRouter } from 'expo-router';
import { useTranslation } from "react-i18next";
import { totpRegisterInit } from "@/src/services/user/totpService";
import DefaultText from "@/src/components/textFields/DefaultText";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import * as Clipboard from 'expo-clipboard';
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import QRCode from "react-native-qrcode-svg";

const SettingsActivateMFA = () => {
    const { t } = useTranslation("settings");
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
                    logo={require("@/assets/images/icon.png")}
                    logoSize={50}
                />
            </View>
            <DefaultText text={t("settings_activate_mfa_cant_scan")} />
            <SecondaryButton text={t("settings_activate_mfa_manual")} onPress={handleCopySecretPress} />
            <DefaultButton text={t("settings_activate_mfa_next")} onPress={() => router.navigate("/(tabs)/overview/(settings)/SettingsMultiFactor")} />
            <DefaultToast />
        </View>
    );
};

export default SettingsActivateMFA;