import React, { useState, useEffect, useCallback } from "react";
import { View, Pressable, Alert, useColorScheme, ScrollView } from "react-native";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { useRouter, useFocusEffect } from "expo-router";
import { useTranslation } from "react-i18next";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "expo-router";
import { asyncLoadData } from "@/src/services/asyncStorageService";
import { getSelfStatus } from "@/src/services/verificiation/identityService";

const SettingsUser: React.FC = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();
    const navigation = useNavigation();

    const [isVerified, setIsVerified] = useState(false);
    const [isPending, setIsPending] = useState(false);

    const moduleTitle = t("userSettingsPageNavigator_title");

    const handleAddressPress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsChangeAddress");
    };

    const handleEmailPress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsChangeEmail");
    };

    const handleUsernamePress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsChangeUsername");
    };

    const handleDeleteUserPress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsDeleteUser");
    };

    const handleNamePress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsChangeName");
    };

    const userTexts = [
        t("settings_name_btn"),
        t("settings_username_btn"),
        t("settings_email_btn"),
        t("settings_address_btn"),
        t("settings_deleteUser_btn")
    ];

    const onPressUserFunctions = [
        handleNamePress,
        handleUsernamePress,
        handleEmailPress,
        handleAddressPress,
        handleDeleteUserPress
    ];

    const userIconNames = ["person", "account-circle", "email", "home", "delete"];

    // Filter out the first option if the user is verified
    const filteredUserTexts = isVerified ? userTexts.slice(1) : userTexts;
    const filteredOnPressUserFunctions = isVerified ? onPressUserFunctions.slice(1) : onPressUserFunctions;
    const filteredUserIconNames = isVerified ? userIconNames.slice(1) : userIconNames;

    // ######################## Account Verification Navigator ######################## //
    // When user taps this, navigate based on verification status
    const verificationTitle = t("accountVerification_title");
    const verificationText = isVerified || isPending
        ? (t("accountVerification_status_btn"))
        : (t("accountVerification_get_btn"));
    const verificationIconName = "verified-user"; // you can change to an appropriate icon

    const handleVerificationPress = () => {
        // If user is verified or pending, navigate to /status, otherwise /getVerified
        if (isVerified || isPending) {
            router.navigate("/(tabs)/overview/(settings)/SettingsVerificationStatus");
        } else {
            router.navigate("/(tabs)/overview/(settings)/SettingsSubmitVerification");
        }
    };

    const [isLight, setIsLight] = useState(false);

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);

    const iconColor = isLight ? "#000000" : "#FFFFFF";

    useEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <Pressable onPress={handleInfoPress}>
                    <Icon
                        name="info"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    const handleInfoPress = () => {
        Alert.alert(
            t("userSettingsPageNavigator_alert_heading"),
            t("userSettingsPageNavigator_subheading"),
            [{ text: "OK" }],
        );
    };

    useFocusEffect(
        useCallback(() => {
            const checkVerifiedStatus = async () => {
                try {
                    const data = await asyncLoadData("isVerified");
                    const verified = data === "true"; // determine verification status locally
                    setIsVerified(verified);
                    if (!verified) {
                        getVerificationStatus(); // only call if not verified
                    }
                } catch (error) {
                    setIsVerified(false);
                    getVerificationStatus(); // call if an error occurred
                }
            };

            const getVerificationStatus = async () => {
                try {
                    const response = await getSelfStatus();
                    setIsPending(response.status === "pending");
                } catch (error) {
                    setIsPending(false);
                }
            };

            checkVerifiedStatus();
        }, [])
    );

    return (
        <ScrollView className="flex h-screen bg-light_primary dark:bg-dark_primary">
            {/* Existing user settings navigator */}
            <PageNavigator
                title={moduleTitle}
                texts={filteredUserTexts}
                iconNames={filteredUserIconNames}
                onPressFunctions={filteredOnPressUserFunctions}
            />

            {/* New account verification navigator */}
            <PageNavigator
                title={verificationTitle}
                texts={[verificationText]}
                iconNames={[verificationIconName]}
                onPressFunctions={[handleVerificationPress]}
            />
        </ScrollView>
    );
};

export default SettingsUser;
