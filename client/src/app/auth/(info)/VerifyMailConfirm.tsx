import React, { useEffect, useRef, useState } from "react";
import { View } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { Confetti } from "react-native-fast-confetti";
import { verifyMail } from "@/src/services/verificiation/verificationService";
import type { ConfettiMethods } from 'react-native-fast-confetti';
import Icon from "react-native-vector-icons/MaterialIcons";

const VerifyMailConfirm = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

    const [color, setColor] = useState("");
    const [icon, setIcon] = useState("");
    const [message, setMessage] = useState("");

    // Get local search parameters from the URL
    const { user_id, expires, signature } = useLocalSearchParams();

    // Create a ref to control the confetti component
    const confettiRef = useRef<ConfettiMethods>(null);

    useEffect(() => {
        const confirmMail = async () => {
            try {
                await verifyMail(
                    typeof user_id === "string"
                        ? user_id
                        : Array.isArray(user_id)
                            ? user_id[0]
                            : "",
                    typeof expires === "string"
                        ? expires
                        : Array.isArray(expires)
                            ? expires[0]
                            : "",
                    typeof signature === "string"
                        ? signature
                        : Array.isArray(signature)
                            ? signature[0]
                            : ""
                );
                setColor("#43a047");
                setIcon("check-circle");
                setMessage(t("verify_email_success"));

                confettiRef.current?.restart();
            } catch (error) {
                setColor("#e53935");
                setIcon("cancel");
                setMessage(t("verify_email_error"));
            }
        };

        confirmMail();
    }, [user_id, expires, signature]);

    const handleBackPress = () => {
        while (router.canGoBack()) {
            router.back();
        }
        router.navigate("/auth");
    };
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <Heading text={message} />
            <Icon name={icon} size={150} color={color} />
            <DefaultButton
                text={t("verify_email_button")}
                onPress={handleBackPress}
            />
            <Confetti ref={confettiRef} isInfinite={false} autoplay={false} />
            <DefaultToast />
        </View>
    );
};

export default VerifyMailConfirm;
