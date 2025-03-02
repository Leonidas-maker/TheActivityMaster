import React, { useState, useEffect } from "react";
import { ScrollView, View, Keyboard, KeyboardAvoidingView, Platform, TouchableWithoutFeedback } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getClub } from "@/src/services/club/clubService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { updateClubName } from "@/src/services/club/clubService";

const ClubUpdateName = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    const { club_id } = useLocalSearchParams();

    const [name, setName] = useState("");
    const [initialName, setInitialName] = useState("");
    const [initialDescription, setInitialDescription] = useState("");
    const [description, setDescription] = useState("");
    const [nameError, setNameError] = useState(false);
    const [descriptionError, setDescriptionError] = useState(false);

    useEffect(() => {
        const fetchClub = async () => {
            try {
                const club = await getClub(club_id);
                setInitialName(club.name);
                setInitialDescription(club.description);
                setName(club.name);
                setDescription(club.description);
            } catch (error) {
                console.error("Error during fetchClub call:", error);
            }
        };
        fetchClub();
    }, []);

    const onUpdatePress = async () => {
        const isNameEmpty = !name.trim();
        const isDescriptionEmpty = !description.trim();

        if (isNameEmpty || isDescriptionEmpty) {
            if (isNameEmpty) setNameError(true);
            if (isDescriptionEmpty) setDescriptionError(true);

            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext")
            });
            return;
        }

        if (name === initialName && description === initialDescription) {
            Toast.show({
                type: "error",
                text1: t("updateError_text"),
                text2: t("updateNameError_subtext")
            });
            return;
        }

        try {
            await updateClubName(club_id, name, description);
            router.back();
        } catch (error) {
            console.error("Error during updateClubName call:", error);
            Toast.show({
                type: "error",
                text1: t("updateErrorCall_text"),
                text2: t("updateErrorCall_subtext")
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="w-full items-center">
                        <View className="py-4">
                            <Heading text={t("creation_step1_title")} />
                        </View>
                        <DefaultTextFieldInput
                            placeholder={t("club_name_placeholder")}
                            value={name}
                            onChangeText={(text) => {
                                setName(text);
                                if (text.trim()) {
                                    setNameError(false);
                                }
                            }}
                            hasError={nameError}
                        />
                        <DefaultTextFieldInput
                            placeholder={t("club_description_placeholder")}
                            value={description}
                            onChangeText={(text) => {
                                setDescription(text);
                                if (text.trim()) {
                                    setDescriptionError(false);
                                }
                            }}
                            hasError={descriptionError}
                        />
                        <DefaultButton text={t("update_name_btn")} onPress={onUpdatePress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
}

export default ClubUpdateName;