import React, { useState, useEffect } from "react";
import { View, KeyboardAvoidingView, Platform, Keyboard, TouchableWithoutFeedback } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { changeName, getUserData } from "@/src/services/user/userService";

const SettingsChangeName = () => {
    const router = useRouter();
    const { t } = useTranslation("settings");

    const [initialFirstName, setInitialFirstName] = useState("");
    const [initialLastName, setInitialLastName] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [firstNameError, setFirstNameError] = useState(false);
    const [lastNameError, setLastNameError] = useState(false);

    // Use useEffect to fetch the user data once when the component mounts
    useEffect(() => {
        async function fetchUserData() {
            const userData = await getUserData();
            // Set the initial values and update the text fields
            setInitialFirstName(userData.first_name);
            setInitialLastName(userData.last_name);
            setFirstName(userData.first_name);
            setLastName(userData.last_name);
        }
        fetchUserData();
    }, []);

    const handleNameChangePress = async () => {
        if (!firstName.trim() || !lastName.trim()) {
            if (!firstName.trim()) {
                setFirstNameError(true);
            }
            if (!lastName.trim()) {
                setLastNameError(true);
            }
            Toast.show({
                type: "error",
                text1: t("error_change_name_all_fields"),
                text2: t("error_fill_all_fields_name_subheading"),
            });
            return;
        }

        if (firstName === initialFirstName && lastName === initialLastName) {
            Toast.show({
                type: "error",
                text1: t("error_change_name_same"),
                text2: t("error_change_name_same_subheading"),
            });
            return;
        }

        try {
            // Call the changeName service
            await changeName(firstName, lastName);

            router.back();
        } catch (error) {
            console.error("Error during changeName call:", error);
            Toast.show({
                type: "error",
                text1: t("error_change_name"),
                text2: t("error_change_name_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("change_name_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("change_firstname_placeholder")}
                        value={firstName}
                        onChangeText={(text) => {
                            setFirstName(text);
                            if (text.trim()) {
                                setFirstNameError(false);
                            }
                        }}
                        hasError={firstNameError}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("change_lastname_placeholder")}
                        value={lastName}
                        onChangeText={(text) => {
                            setLastName(text);
                            if (text.trim()) {
                                setLastNameError(false);
                            }
                        }}
                        hasError={lastNameError}
                    />
                    <DefaultButton text={t("change_name_button")} onPress={handleNameChangePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsChangeName;
