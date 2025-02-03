import React, { useState, useEffect } from "react";
import {
  ScrollView,
  Keyboard,
  TouchableWithoutFeedback,
  View,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  StyleSheet,
  Text,
} from "react-native";
import { useTranslation } from "react-i18next";
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
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";

const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [saveLogin, setSaveLogin] = useState(true);
  const [isLoginLoading, setIsLoginLoading] = useState(true);

  // States to track if an input field is empty
  const [usernameError, setUsernameError] = useState(false);
  const [passwordError, setPasswordError] = useState(false);

  const { t } = useTranslation("auth");
  const router = useRouter();       

  const loggedInTitle = t("saveLoginData_title");
  const loggedInText = [t("saveLoginData_text")];
  const loggedInIcon = ["history"];

  // Login handler with validation and highlighting of empty fields
  const loginPress = () => {
    let hasError = false;

    if (!username.trim()) {
      setUsernameError(true);
      hasError = true;
    }

    if (!password.trim()) {
      setPasswordError(true);
      hasError = true;
    }

    if (hasError) {
      Toast.show({
        type: "error",
        text1: t("inputError_text"),
        text2: t("inputError_subtext"),
        autoHide: false
      });
      return;
    }

    // Reset error states if inputs are correct
    setUsernameError(false);
    setPasswordError(false);

    router.replace("/(tabs)");
    if (saveLogin) {
      saveCredentials();
    }
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

  // Load the saveLogin state from AsyncStorage when the component mounts
  useEffect(() => {
    const loadSavedLogin = async () => {
      const savedSaveLogin = await asyncLoadData("saveAppLogin");

      if (savedSaveLogin !== null) {
        setSaveLogin(JSON.parse(savedSaveLogin)); // Convert string back to boolean
      }
    };

    loadSavedLogin();
  }, []);

  // Save the saveLogin state to AsyncStorage whenever it changes
  useEffect(() => {
    asyncSaveData("saveAppLogin", JSON.stringify(saveLogin));
  }, [saveLogin]);

  // Toggle the saveLogin switch
  const toggleSaveLogin = () => {
    setSaveLogin(!saveLogin);

    // Remove login credentials if saveLogin is disabled
    if (!saveLogin === false) {
      removeCredentials();
    } else {
      saveCredentials();
    }
  };

  // Load saved credentials when the component mounts
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

  // Wait until login data is loaded (this usually happens very quickly)
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
              onChangeText={(text) => {
                setUsername(text);
                if (text.trim()) {
                  setUsernameError(false);
                }
              }}
              autoCapitalize="none"
              hasError={usernameError}
            />
            <DefaultTextFieldInput
              placeholder={t("password_textfield")}
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                if (text.trim()) {
                  setPasswordError(false);
                }
              }}
              secureTextEntry
              hasError={passwordError}
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
              <SecondaryButton
                text={t("toRegister_button")}
                onPress={() => router.navigate("/auth/SignUp")}
              />
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
      <DefaultToast />
    </KeyboardAvoidingView>
  );
};

export default Login;
