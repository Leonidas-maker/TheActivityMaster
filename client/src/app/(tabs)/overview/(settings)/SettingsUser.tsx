import React, { useState, useEffect } from "react";
import { View, Text } from "react-native";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

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

    const userTexts = [t("settings_username_btn"), t("settings_email_btn"), t("settings_address_btn"), t("settings_deleteUser_btn")];

    const onPressUserFunctions = [handleUsernamePress, handleEmailPress, handleAddressPress, handleDeleteUserPress];

    const userIconNames = ["account-circle", "email", "home", "delete"];

    return (
        <View className="flex h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={moduleTitle}
                texts={userTexts}
                iconNames={userIconNames}
                onPressFunctions={onPressUserFunctions}
            />
        </View>
    );
};

export default SettingsUser;
