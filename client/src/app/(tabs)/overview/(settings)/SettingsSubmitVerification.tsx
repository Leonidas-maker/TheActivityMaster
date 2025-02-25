import React, { useState } from "react";
import { View, Image, Alert, ScrollView, KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard } from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as ImageManipulator from "expo-image-manipulator";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { submitIdentityVerification } from "@/src/services/verificiation/identityService";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import Subheading from "@/src/components/textFields/Subheading";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

//TODO: Add mrz scanning
const SettingsSubmitVerification = () => {
    const { t } = useTranslation("settings");
    const router = useRouter();

    // State for the three images
    const [frontImage, setFrontImage] = useState<string | null>(null);
    const [backImage, setBackImage] = useState<string | null>(null);
    const [selfieImage, setSelfieImage] = useState<string | null>(null);
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [dateOfBirth, setDateOfBirth] = useState("");
    const [firstNameError, setFirstNameError] = useState(false);
    const [lastNameError, setLastNameError] = useState(false);
    const [dateOfBirthError, setDateOfBirthError] = useState(false);

    // Function to convert an image to PNG format using Expo ImageManipulator
    const convertImageToPng = async (uri: string) => {
        try {
            const result = await ImageManipulator.manipulateAsync(
                uri,
                [], // no transformations, just a format change
                { compress: 1, format: ImageManipulator.SaveFormat.PNG }
            );
            return result.uri;
        } catch (error) {
            console.error("Error converting image:", error);
            return uri; // fallback to original URI if conversion fails
        }
    };

    // Generic function to pick an image from the library
    const pickImage = async (setImage: React.Dispatch<React.SetStateAction<string | null>>) => {
        const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!permissionResult.granted) {
            Alert.alert("Permission required", "Permission to access camera roll is required!");
            return;
        }
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: "images",
            allowsEditing: false,
            quality: 1,
        });
        if (!result.canceled) {
            const pngUri = await convertImageToPng(result.assets[0].uri);
            setImage(pngUri);
        }
    };

    // Function to handle the submission process
    const handleSubmit = async () => {
        if (!frontImage || !backImage || !selfieImage) {
            Toast.show({
                type: "error",
                text1: t("error_submit_verification"),
                text2: t("error_submit_verification_subheading"),
            });
            return;
        }

        if (!firstName.trim() || !lastName.trim() || !dateOfBirth.trim()) {
            if (!firstName.trim()) {
                setFirstNameError(true);
            }
            if (!lastName.trim()) {
                setLastNameError(true);
            }
            if (!dateOfBirth.trim()) {
                setDateOfBirthError(true);
            }

            Toast.show({
                type: "error",
                text1: t("error_missing_fields"),
                text2: t("error_missing_fields_subheading"),
            });
            return;
        }

        const id_card_mrz = "sample_mrz";

        try {
            const response = await submitIdentityVerification({
                front_image: frontImage,
                rear_image: backImage,
                selfie_image: selfieImage,
                id_card_mrz,
                first_name: firstName,
                last_name: lastName,
                date_of_birth: dateOfBirth,
            });
            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/");
        } catch (error) {
            console.error("Error during submitIdentityVerification call:", error);
            Toast.show({
                type: "error",
                text1: t("error_submit_verification_failed"),
                text2: t("error_submit_verification_failed_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="flex h-full bg-light_primary dark:bg-dark_primary">
                    <View className="items-center justify-center">
                        <View className="py-4">
                            <Heading text={t("submit_verification")} />
                        </View>
                        <DefaultTextFieldInput
                            placeholder={t("first_name_placeholder_verify")}
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
                            placeholder={t("last_name_placeholder_verify")}
                            value={lastName}
                            onChangeText={(text) => {
                                setLastName(text);
                                if (text.trim()) {
                                    setLastNameError(false);
                                }
                            }}
                            hasError={lastNameError}
                        />
                        <DefaultTextFieldInput
                            placeholder={t("dob_placeholder_verify")}
                            value={dateOfBirth}
                            onChangeText={(text) => {
                                setDateOfBirth(text);
                                if (text.trim()) {
                                    setDateOfBirthError(false);
                                }
                            }}
                            hasError={dateOfBirthError}
                        />

                        {/* Front of ID */}
                        <Subheading text={t("front_id_sub")} />
                        {frontImage && (
                            <Image source={{ uri: frontImage }} style={{ width: "100%", height: 200, marginBottom: 10 }} />
                        )}
                        <SecondaryButton text={t("select_front_image")} onPress={() => pickImage(setFrontImage)} />

                        {/* Back of ID */}
                        <Subheading text={t("back_id_sub")} />
                        {backImage && (
                            <Image source={{ uri: backImage }} style={{ width: "100%", height: 200, marginBottom: 10 }} />
                        )}
                        <SecondaryButton text={t("select_back_image")} onPress={() => pickImage(setBackImage)} />

                        {/* Selfie with ID */}
                        <Subheading text={t("selfie_id_sub")} />
                        {selfieImage && (
                            <Image source={{ uri: selfieImage }} style={{ width: "100%", height: 200, marginBottom: 10 }} />
                        )}
                        <SecondaryButton text={t("select_selfie_image")} onPress={() => pickImage(setSelfieImage)} />

                        {/* Submit Verification */}
                        <DefaultButton text={t("submit_verification_button")} onPress={handleSubmit} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default SettingsSubmitVerification;
