import React, { useState, useEffect } from "react";
import { View, ScrollView, KeyboardAvoidingView, Platform, Keyboard, TouchableWithoutFeedback } from "react-native";
import { useTranslation } from 'react-i18next';
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { useRouter } from "expo-router";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
import Subheading from "@/src/components/textFields/Subheading";
import Dropdown from "@/src/components/dropdown/Dropdown";

const SignUp: React.FC = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();

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
                        <DefaultText text={t("login_title")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_password_placeholder")} secureTextEntry={true} />
                        <DefaultTextFieldInput placeholder={t("login_password_placeholder")} secureTextEntry={true} />
                        <Subheading text={t("login_subheading")} />
                        <Dropdown values={[]} setSelected={() => ""} search={true} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <DefaultTextFieldInput placeholder={t("login_email_placeholder")} />
                        <OptionSwitch title={t("login_loggedIn_title")} texts={[t("login_loggedIn_text")]} iconNames={["save"]} values={[true]} onValueChanges={[() => { }]} />
                        <DefaultButton text={t("login_btn")} onPress={() => router.replace("/(tabs)")} />
                        <View className="mb-12 w-full justify-center items-center">
                            <SecondaryButton text={t("login_register_btn")} onPress={() => router.navigate("/auth")} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SignUp;
