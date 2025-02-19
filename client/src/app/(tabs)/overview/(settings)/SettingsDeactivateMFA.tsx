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

const SettingsDeactivateMFA = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <View className="py-4">
                <Heading text={t("settings_deactivate_mfa_heading")} />
            </View>
            <DefaultText text={t("settings_deactivate_mfa_description")} />
            <DefaultButton text={t("settings_deactivate_mfa_next")} onPress={() => router.navigate("/(tabs)/overview/(settings)/SettingsMultiFactor")} />
            <DefaultToast />
        </View>
    );
};

export default SettingsDeactivateMFA;