import React, { useState, useEffect, useCallback } from "react";
import { View, Pressable, Alert, useColorScheme } from "react-native";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { useRouter, useFocusEffect } from "expo-router";
import { useTranslation } from "react-i18next";
import DefaultText from "@/src/components/textFields/DefaultText";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "expo-router";
import { asyncLoadData } from "@/src/services/asyncStorageService";

const SettingsUser: React.FC = () => {
    /* // State to store the response as a string
    const [username, setUsername] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [country, setCountry] = useState("");
    const [city, setCity] = useState("");
    const [street, setStreet] = useState("");
    const [zipCode, setZipCode] = useState("");
    const [state, setState] = useState(""); */

    /* useEffect(() => {
        // Fetch user data and update the state
        getUserData().then((data) => {
            setUsername(data.username);
            setFirstName(data.first_name);
            setLastName(data.last_name);
            setEmail(data.email);
            if (data.address) {
                setCountry(data.address.country);
                setCity(data.address.city);
                setStreet(data.address.street);
                setZipCode(data.address.postal_code);
                setState(data.address.state);
            }
        });
    }, []); */

    const { t } = useTranslation("settings");
    const router = useRouter();
    const navigation = useNavigation();

    const [isVerified, setIsVerified] = useState(false);

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

    const userTexts = [t("settings_name_btn"), t("settings_username_btn"), t("settings_email_btn"), t("settings_address_btn"), t("settings_deleteUser_btn")];

    const onPressUserFunctions = [handleNamePress, handleUsernamePress, handleEmailPress, handleAddressPress, handleDeleteUserPress];

    const userIconNames = ["person", "account-circle", "email", "home", "delete"];

    // Filter out the user option (index 0) if the user is verified
    const filteredUserTexts = isVerified ? userTexts.slice(1) : userTexts;
    const filteredOnPressUserFunctions = isVerified ? onPressUserFunctions.slice(1) : onPressUserFunctions;
    const filteredUserIconNames = isVerified ? userIconNames.slice(1) : userIconNames;

    const [isLight, setIsLight] = useState(false);

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    // Get the current color scheme
    const colorScheme = useColorScheme();

    // Check if the color scheme is light or dark
    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    // Set the icon color based on the color scheme
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // Set the header button dynamically
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
    }, [navigation, colorScheme]);

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
                    // Convert the string to boolean
                    setIsVerified(data === "true");
                } catch (error) {
                    setIsVerified(false);
                }
            };
            checkVerifiedStatus();
        }, [])
    );

    return (
        <View className="flex h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={moduleTitle}
                texts={filteredUserTexts}
                iconNames={filteredUserIconNames}
                onPressFunctions={filteredOnPressUserFunctions}
            />
        </View>
    );
};

export default SettingsUser;
