import React, { useEffect, useState } from "react";
import { Alert, ScrollView, View } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { getSelfStatus, deleteSelfVerification } from "@/src/services/verificiation/identityService";
import dayjs from "dayjs";

const SettingsVerificationStatus = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();
    const [status, setStatus] = useState("");
    const [verifiedAt, setVerifiedAt] = useState("");
    const [expiresAt, setExpiresAt] = useState("");

    useEffect(() => {
        const fetchStatus = async () => {
            const response = await getSelfStatus();

            if (response.status === "pending") {
                setStatus("pending");
            } else if (response.status === "approved") {
                setStatus("approved");

                if (response.created_at) {
                    setVerifiedAt(dayjs(response.created_at).format("DD.MM.YYYY"));
                }
                if (response.expires_at) {
                    setExpiresAt(dayjs(response.expires_at).format("DD.MM.YYYY"));
                }
            }
        };
        fetchStatus();
    }, []);

    const handleDeletePress = async () => {
        Alert.alert(t("delete_verification_alert_title"), t("delete_verification_alert_text"), [
            {
                text: t("cancel"),
                style: "cancel",
            },
            {
                text: t("delete_verification"),
                onPress: () => handleDelete(),
            },
        ]);
    };

    const handleDelete = async () => {
        await deleteSelfVerification();

        while (router.canGoBack()) {
            router.back();
        }
    }

    return (
        <ScrollView className="flex h-screen bg-light_primary dark:bg-dark_primary">
            <View className="py-4">
                <Heading text={t("verification_status")} />
            </View>
            {status === "pending" && (
                <View className="items-center justify-center px-4">
                    <DefaultText text={t("verification_status_pending_text")} />
                </View>
            )}
            {status === "approved" && (
                <View className="items-center justify-center px-4">
                    <DefaultText text={t("verification_status_approved_text")} />
                    {verifiedAt !== "" && (
                        <View className="py-2">
                            <DefaultText text={t("verification_status_verified_at") + verifiedAt} />
                        </View>
                    )}
                    {expiresAt !== "" && (
                            <DefaultText text={t("verification_status_expires_at") + expiresAt} />
                    )}
                </View>
            )}
            <View className="items-center justify-center py-4">
                <DefaultButton text={t("delete_verification_button")} onPress={handleDeletePress} />
            </View>
        </ScrollView>
    );
};

export default SettingsVerificationStatus;
