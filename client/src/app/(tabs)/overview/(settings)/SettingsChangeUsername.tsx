import React, { useState } from "react";
import { View, KeyboardAvoidingView, TouchableWithoutFeedback, Platform, Keyboard } from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { changeUsername } from "@/src/services/user/userService";

const SettingsChangeUsername = () => {
    const router = useRouter();
    const { t } = useTranslation("settings");

    const [password, setPassword] = useState("");
    const [newUsername, setNewUsername] = useState("");
    const [newUsernameError, setNewUsernameError] = useState(false);
    const [passwordError, setPasswordError] = useState(false);

    const handleUsernameChangePress = async () => {
        if (!newUsername.trim() || !password.trim()) {
            if (!newUsername.trim()) {
                setNewUsernameError(true);
            }
            if (!password.trim()) {
                setPasswordError(true);
            }
            Toast.show({
                type: "error",
                text1: t("error_change_username_all_fields"),
                text2: t("error_fill_all_fields_username_subheading"),
            });
            return;
        }

        try {
            // Call the changeUsername service
            await changeUsername(newUsername, password);

            router.back();
        } catch (error) {
            console.error("Error during changeUsername call:", error);
            Toast.show({
                type: "error",
                text1: t("error_change_username"),
                text2: t("error_change_username_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("change_username_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("change_username_placeholder")}
                        value={newUsername}
                        onChangeText={(text) => {
                            setNewUsername(text);
                            if (text.trim()) {
                                setNewUsernameError(false);
                            }
                        }}
                        hasError={newUsernameError}
                    />
                    <DefaultTextFieldInput
                        secureTextEntry={true}
                        placeholder={t("change_username_password_placeholder")}
                        value={password}
                        onChangeText={(text) => {
                            setPassword(text);
                            if (text.trim()) {
                                setPasswordError(false);
                            }
                        }}
                        hasError={passwordError}
                    />
                    <DefaultButton text={t("change_username_button")} onPress={handleUsernameChangePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};


export default SettingsChangeUsername;