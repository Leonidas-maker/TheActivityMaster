import React, { useState, useEffect } from "react";
import {
    ScrollView,
    View,
    KeyboardAvoidingView,
    TouchableWithoutFeedback,
    Keyboard,
    Platform,
    useColorScheme, 
    Pressable
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";
import Dropdown from "@/src/components/dropdown/Dropdown";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import { getPrograms } from "@/src/services/club/programService";
import { createMembershipAccess } from "@/src/services/club/membershipService";
import Subheading from "@/src/components/textFields/Subheading";
import Icon from "react-native-vector-icons/MaterialIcons";

const AddProgramMembershipAccess = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, membership_id } = useLocalSearchParams();

    // State for programs list and loading indicator
    const [programs, setPrograms] = useState([]);
    const [loading, setLoading] = useState(false);

    // Form state
    const [selectedProgram, setSelectedProgram] = useState("");
    const [additionalFee, setAdditionalFee] = useState("");

    // Error states
    const [programError, setProgramError] = useState(false);
    const [feeError, setFeeError] = useState(false);

    // Color scheme state
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            )
        });
    }, [navigation, iconColor]);

    // Fetch programs when the component mounts
    useEffect(() => {
        if (club_id) {
            setLoading(true);
            // Assuming a page size that retrieves all available programs
            getPrograms(club_id, 1, 50)
                .then((data) => {
                    setPrograms(data);
                })
                .catch((error) => {
                    console.error("Error fetching programs:", error);
                    Toast.show({
                        type: "error",
                        text1: t("roleManageError"),
                        text2: t("roleManageErrorDescription")
                    });
                })
                .finally(() => {
                    setLoading(false);
                });
        }
    }, [club_id, t]);

    const handleCreateMembershipAccessPress = async () => {
        // Reset errors
        setProgramError(false);
        setFeeError(false);

        let hasError = false;

        if (!selectedProgram) {
            setProgramError(true);
            hasError = true;
        }
        if (additionalFee.trim() && isNaN(Number(additionalFee))) {
            setFeeError(true);
            hasError = true;
        }

        if (hasError) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext")
            });
            return;
        }

        const feeValue = additionalFee.trim() === "" ? 0 : Number(additionalFee);

        try {
            await createMembershipAccess(club_id, membership_id, selectedProgram, feeValue);
            router.dismiss();
        } catch (error) {
            console.error("Error creating membership access:", error);
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center py-4">
                        <Heading text={t("createMembershipAccess_heading")} />
                        <Subheading text={t("createMembershipAccess_subheading")} />
                        {loading ? (
                            <DefaultText text={t("loading")} />
                        ) : programs.length === 0 ? (
                            // Inform the user to create a program first if none exist
                            <DefaultText text={t("noPrograms_message")} />
                        ) : (
                            <>
                                <Dropdown
                                    setSelected={(selected) => {
                                        setSelectedProgram(selected);
                                        if (selected) setProgramError(false);
                                    }}
                                    values={programs.map((program: any) => ({
                                        key: program.id,
                                        value: program.name
                                    }))}
                                    placeholder={t("selectProgram_placeholder")}
                                    save="key"
                                    search={true}
                                />
                                <View className="items-center px-4">
                                    <DefaultText text={t("additionalFee_text")} />
                                </View>
                                <DefaultTextFieldInput
                                    placeholder={t("additionalFee_placeholder")}
                                    value={additionalFee}
                                    onChangeText={(text) => {
                                        setAdditionalFee(text);
                                        if (text.trim() && !isNaN(Number(text))) {
                                            setFeeError(false);
                                        }
                                    }}
                                    hasError={feeError}
                                />
                                <DefaultButton
                                    text={t("createMembershipAccess_btn")}
                                    onPress={handleCreateMembershipAccessPress}
                                />
                            </>
                        )}
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddProgramMembershipAccess;