import React, { useCallback, useState } from "react";
import { View } from "react-native";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useFocusEffect } from "expo-router";
import { getUserData, updateNewsletterSubscription } from "@/src/services/user/userService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

const SettingsNotifications = () => {
    const { t } = useTranslation("settings");

    const [receiveNews, setReceiveNews] = useState(false);

    useFocusEffect(
        useCallback(() => {
            const fetchData = async () => {
                try {
                    const user = await getUserData();
                    setReceiveNews(user.is_newsletter_subscribed);
                } catch (error) {
                    console.error("Error fetching user data:", error);
                }
            };
            fetchData();
        }, [])
    );

    const handleReceiveNewsChange = async (newValue: boolean) => {
        setReceiveNews(newValue);
        try {
            await updateNewsletterSubscription(newValue);
        } catch (error) {
            console.error("Error updating newsletter subscription:", error);
            Toast.show({
                type: "error",
                text1: t("settings_receive_news_error"),
                text2: t("settings_receive_news_error_subheading"),
            });
            setReceiveNews(!newValue);
        }
    };

    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <View className="py-4">
                <Heading text={t("settings_receive_notification_header")} />
            </View>
            <OptionSwitch
                title={t("receive_news")}
                texts={[t("receive_news_text")]}
                iconNames={["newspaper"]}
                values={[receiveNews]}
                onValueChanges={[handleReceiveNewsChange]}
            />
            <DefaultToast />
        </View>
    );
};

export default SettingsNotifications;
