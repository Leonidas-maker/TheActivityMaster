import React, { useState, useEffect } from "react";
import { ScrollView, Keyboard, TouchableWithoutFeedback, View, KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { useTranslation } from 'react-i18next';
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { useRouter } from "expo-router";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
import { asyncLoadData, asyncRemoveData, asyncSaveData } from "@/src/services/asyncStorageService";
import { secureLoadData, secureRemoveData, secureSaveData } from "@/src/services/secureStorageService";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import Subheading from "@/src/components/textFields/Subheading";
import Heading from "@/src/components/textFields/Heading";

const Login: React.FC = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [saveLogin, setSaveLogin] = useState(true);
    const [isLoginLoading, setIsLoginLoading] = useState(true);

    const { t } = useTranslation("auth");
    const router = useRouter();

    const loggedInTitle = t("saveLoginData_title");
    const loggedInText = [t("saveLoginData_text")];
    const loggedInIcon = ["history"];

    const loginPress = () => {
        router.replace("/(tabs)");
        if (saveLogin) {
            saveCredentials();
        };
    };

    // Function to save login credentials
    const saveCredentials = () => {
        asyncSaveData("savedUsername", username);
        secureSaveData("savedPassword", password);
    };

    // Function to remove login credentials
    const removeCredentials = async () => {
        asyncRemoveData("savedUsername");
        secureRemoveData("savedPassword");
    };

    // Load saveLogin state from AsyncStorage when component mounts
    useEffect(() => {
        const loadSavedLogin = async () => {
            const savedSaveLogin = await asyncLoadData("saveAppLogin");

            if (savedSaveLogin !== null) {
                setSaveLogin(JSON.parse(savedSaveLogin)); // Convert string back to boolean
            }
        };

        loadSavedLogin();
    }, []);

    // Save saveLogin state to AsyncStorage when it changes
    useEffect(() => {
        asyncSaveData("saveAppLogin", JSON.stringify(saveLogin));
    }, [saveLogin]);

    // Toggles the save login switch
    const toggleSaveLogin = () => {
        setSaveLogin(!saveLogin);

        // Remove credentials if saveLogin is disabled
        if (!saveLogin === false) {
            removeCredentials();
        } else {
            saveCredentials();
        }
    };

    // Load saved credentials when component mounts
    useEffect(() => {
        const loadCredentials = async () => {
            const savedUsername = await asyncLoadData("savedUsername");
            const savedPassword = await secureLoadData("savedPassword");

            if (savedUsername) setUsername(savedUsername);
            if (savedPassword) setPassword(savedPassword);

            setIsLoginLoading(false);
        };

        if (saveLogin) {
            loadCredentials();
        } else {
            setIsLoginLoading(false);
        }
    }, [saveLogin]);

    // Wait for login data to load (this is very fast so it will most likely not be shown very long)
    if (isLoginLoading) {
        return (
            <View className="h-screen bg-light_primary dark:bg-dark_primary flex-1 justify-center items-center">
                <ActivityIndicator size="large" color="#0000ff" />
                <DefaultText text={t("loadCredential_text")} />
            </View>
        );
    }

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView
                    className="h-screen bg-light_primary dark:bg-dark_primary"
                    keyboardShouldPersistTaps="handled"
                    contentContainerStyle={{ flexGrow: 1 }}
                >
                    <View className="flex justify-center items-center pt-4">
                        <View className="py-4">
                            <Heading text={t("login_title")} />
                        </View>
                        <DefaultTextFieldInput
                            placeholder={t("username_textfield")}
                            value={username}
                            onChangeText={setUsername}
                            autoCapitalize="none"
                        />
                        <DefaultTextFieldInput
                            placeholder={t("password_textfield")}
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />

                        <DefaultButton text={t("login_button")} onPress={loginPress} />
                        <OptionSwitch
                            title={loggedInTitle}
                            onValueChanges={[toggleSaveLogin]}
                            texts={loggedInText}
                            iconNames={loggedInIcon}
                            values={[saveLogin]}
                        />
                        <View className="mb-12 w-full justify-center items-center">
                            <SecondaryButton text={t("toRegister_button")} onPress={() => router.navigate("/auth/SignUp")} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default Login;
