import React, { useState, useEffect, useCallback } from "react";
import {
    ScrollView,
    View,
    useColorScheme,
    Pressable,
    Keyboard,
    KeyboardAvoidingView,
    Platform,
    TouchableWithoutFeedback,
    Alert
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import { cancelOccurrence, reinstateOccurrence, rescheduleOccurrence } from "@/src/services/club/programSessionOccurrenceService";
import DateTimePicker from "@/src/components/picker/DateTimePicker";
import Subheading from "@/src/components/textFields/Subheading";

// Helper function to extract string value from a parameter
const getParamValue = (param: string | string[] | undefined): string => {
    if (typeof param === "string") {
        return param;
    }
    if (Array.isArray(param) && param.length > 0) {
        return param[0];
    }
    return "";
};

const ManageOccurrence = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const {
        club_id,
        program_id,
        session_id,
        occurrence_id,
        occurrence_status,
        start_datetime,
        end_datetime,
        note
    } = useLocalSearchParams();

    // Extract and set default parameter values
    const occurrenceStatus = getParamValue(occurrence_status);
    const defaultNote = getParamValue(note) === "undefined" ? "" : getParamValue(note);
    const defaultStart = start_datetime && start_datetime !== "undefined" ? new Date(getParamValue(start_datetime)) : new Date();
    const defaultEnd = end_datetime && end_datetime !== "undefined" ? new Date(getParamValue(end_datetime)) : new Date();
    const defaultDate = defaultStart;

    // Theme state
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = useCallback(() => {
        router.dismiss();
    }, [router]);

    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon name="close" size={30} color={iconColor} style={{ marginLeft: "auto", marginRight: 15 }} />
                </Pressable>
            )
        });
    }, [navigation, iconColor, handleDismissPress]);

    // State for rescheduling fields (used for both 'scheduled' and 'rescheduled' occurrences)
    const [rescheduleDate, setRescheduleDate] = useState(defaultDate);
    const [rescheduleStartTime, setRescheduleStartTime] = useState(defaultStart);
    const [rescheduleEndTime, setRescheduleEndTime] = useState(defaultEnd);
    // For reschedule note, default is empty
    const [rescheduleNote, setRescheduleNote] = useState(
        (occurrenceStatus === "rescheduled") ? defaultNote : ""
    );

    // State for cancellation and reinstatement notes
    // For cancel note, default is empty
    const [cancelNote, setCancelNote] = useState(
        (occurrenceStatus === "cancelled") ? defaultNote : ""
    );
    // For reinstate note, default is set to defaultNote only when status is scheduled or rescheduled.
    const [reinstateNote, setReinstateNote] = useState("");


    // Handler for rescheduling occurrence with validation
    const handleRescheduleOccurrence = async () => {
        // Combine date and time from pickers for start and end times
        const newStart = new Date(
            rescheduleDate.getFullYear(),
            rescheduleDate.getMonth(),
            rescheduleDate.getDate(),
            rescheduleStartTime.getHours(),
            rescheduleStartTime.getMinutes(),
            rescheduleStartTime.getSeconds()
        );
        const newEnd = new Date(
            rescheduleDate.getFullYear(),
            rescheduleDate.getMonth(),
            rescheduleDate.getDate(),
            rescheduleEndTime.getHours(),
            rescheduleEndTime.getMinutes(),
            rescheduleEndTime.getSeconds()
        );

        // Validate that the new end time is after the new start time
        if (newStart >= newEnd) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_time")
            });
            return;
        }

        try {
            await rescheduleOccurrence(
                club_id,
                program_id,
                session_id,
                occurrence_id,
                rescheduleNote.trim(),
                newStart.toISOString(),
                newEnd.toISOString()
            );
            for (let i = 0; i < 2; i++) {
                router.back()
            }
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    // Handler for cancelling occurrence with confirmation
    const handleCancelOccurrence = async () => {
        Alert.alert(
            t("cancel_occurrence"),
            t("cancel_occurrence_confirmation"),
            [
                {
                    text: t("cancel_btn"),
                    style: "cancel"
                },
                {
                    text: t("confirm_btn"),
                    onPress: async () => {
                        try {
                            await cancelOccurrence(club_id, program_id, session_id, occurrence_id, cancelNote.trim());
                            for (let i = 0; i < 2; i++) {
                                router.back()
                            }
                        } catch (error) {
                            Toast.show({
                                type: "error",
                                text1: t("roleManageError"),
                                text2: t("roleManageErrorDescription")
                            });
                        }
                    }
                }
            ]
        );
    };

    // Handler for reinstating occurrence
    const handleReinstateOccurrence = async () => {
        try {
            await reinstateOccurrence(club_id, program_id, session_id, occurrence_id, reinstateNote.trim());
            for (let i = 0; i < 2; i++) {
                router.back()
            }
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="pt-4">
                            <Heading text={t("manage_occurrence")} />
                        </View>
                        {/* Reschedule Section: shown for 'scheduled' and 'rescheduled' statuses */}
                        {(occurrenceStatus === "scheduled" || occurrenceStatus === "rescheduled") && (
                            <>
                                <Subheading text={t("reschedule_occurrence")} />
                                <DefaultText text={t("occurrence_date")} />
                                <DateTimePicker
                                    mode="date"
                                    value={rescheduleDate}
                                    onConfirm={setRescheduleDate}
                                    minimumDate={new Date()}
                                />
                                <DefaultText text={t("start_time")} />
                                <DateTimePicker
                                    mode="time"
                                    value={rescheduleStartTime}
                                    onConfirm={setRescheduleStartTime}
                                />
                                <DefaultText text={t("end_time")} />
                                <DateTimePicker
                                    mode="time"
                                    value={rescheduleEndTime}
                                    onConfirm={setRescheduleEndTime}
                                />
                                <DefaultTextFieldInput
                                    placeholder={t("enter_note_rescheduling")}
                                    value={rescheduleNote}
                                    onChangeText={(text) => setRescheduleNote(text)}
                                />
                                <DefaultButton text={t("reschedule_occurrence")} onPress={handleRescheduleOccurrence} />
                            </>
                        )}

                        {/* Reinstate Section: shown for 'rescheduled' and 'cancelled' statuses */}
                        {(occurrenceStatus === "rescheduled" || occurrenceStatus === "cancelled") && (
                            <>
                                <Subheading text={t("reinstate_occurrence")} />
                                <DefaultTextFieldInput
                                    placeholder={t("enter_note_reinstatement")}
                                    value={reinstateNote}
                                    onChangeText={(text) => setReinstateNote(text)}
                                />
                                <DefaultButton text={t("reinstate_occurrence")} onPress={handleReinstateOccurrence} />
                            </>
                        )}

                        {/* Cancellation Section: shown for 'scheduled' and 'rescheduled' statuses */}
                        {(occurrenceStatus === "scheduled" || occurrenceStatus === "rescheduled") && (
                            <>
                                <Subheading text={t("cancel_occurrence")} />
                                <DefaultTextFieldInput
                                    placeholder={t("enter_note_cancellation")}
                                    value={cancelNote}
                                    onChangeText={(text) => setCancelNote(text)}
                                />
                                <DefaultButton text={t("cancel_occurrence")} onPress={handleCancelOccurrence} />
                            </>
                        )}

                        <DefaultToast />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default ManageOccurrence;