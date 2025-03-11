import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
    ScrollView,
    View,
    Pressable,
    useColorScheme,
    Keyboard,
    KeyboardAvoidingView,
    Platform,
    TouchableWithoutFeedback
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import DateTimePicker from "@/src/components/picker/DateTimePicker";
import Subheading from "@/src/components/textFields/Subheading";
import { updateSession, deleteSession } from "@/src/services/club/programSessionService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

// Helper function to extract a string value from a search param that could be a string or string[]
const getParamValue = (param: string | string[] | undefined): string => {
    if (typeof param === "string") {
        return param;
    }
    if (Array.isArray(param) && param.length > 0) {
        return param[0];
    }
    return "";
};

const ManageEvent = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const {
        club_id,
        program_id,
        session_id,
        pricing_model,
        start_date,
        end_date,
        capacity_event,
        price_event
    } = useLocalSearchParams();

    // Use the query parameters for date/time values
    const startDateStr = getParamValue(start_date);
    const endDateStr = getParamValue(end_date);

    // Initialize start and end time using provided query parameters; fallback to current date/time if not provided.
    const initialStartDateTime = startDateStr ? new Date(startDateStr) : new Date();
    const initialEndDateTime = endDateStr ? new Date(endDateStr) : new Date();

    // Extract the event date as the date part of the start_date if provided, otherwise default to current date.
    const initialEventDate = startDateStr ? new Date(startDateStr.split("T")[0]) : new Date();

    // Store initial values for later change comparison.
    const initialPrice = getParamValue(price_event);
    const initialCapacity = getParamValue(capacity_event);

    const [price, setPrice] = useState(initialPrice);
    const [priceError, setPriceError] = useState(false);
    const [capacity, setCapacity] = useState(initialCapacity);
    const [capacityError, setCapacityError] = useState(false);
    const [note, setNote] = useState("");
    const [noteError, setNoteError] = useState(false);

    // States for the time pickers using the values from query parameters.
    const [startEventTime, setStartEventTime] = useState(initialStartDateTime);
    const [endEventTime, setEndEventTime] = useState(initialEndDateTime);

    // States for the DatePicker using the event date.
    const [eventDate, setEventDate] = useState(initialEventDate);

    // Update date/time state if query parameters change
    useEffect(() => {
        if (startDateStr) {
            const newStart = new Date(startDateStr);
            setStartEventTime(newStart);
            // Also update the event date if needed
            setEventDate(new Date(startDateStr.split("T")[0]));
        }
        if (endDateStr) {
            setEndEventTime(new Date(endDateStr));
        }
    }, [startDateStr, endDateStr]);

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
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor, handleDismissPress]);

    // Calculate minimum date for event date picker: tomorrow
    const tomorrow = useMemo(() => {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        return date;
    }, []);

    // Handler for delete button remains unchanged.
    const handleDeletePress = async () => {
        try {
            await deleteSession(club_id, program_id, session_id, note);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
        }
    };

    // Handler for update button with change checking and date formatting.
    const handleUpdatePress = async () => {
        // Check if any of the key fields have changed
        if (
            price === initialPrice &&
            capacity === initialCapacity &&
            startEventTime.getTime() === initialStartDateTime.getTime() &&
            endEventTime.getTime() === initialEndDateTime.getTime() &&
            eventDate.toISOString().split("T")[0] === initialEventDate.toISOString().split("T")[0]
        ) {
            Toast.show({
                type: "info",
                text1: t("noChangesMade"),
                text2: t("noChangesDescription"),
            });
            return;
        }

        const eventStartDateTime = new Date(
            Date.UTC(
                eventDate.getFullYear(),
                eventDate.getMonth(),
                eventDate.getDate(),
                startEventTime.getHours(),
                startEventTime.getMinutes(),
                startEventTime.getSeconds()
            )
        );
        const eventEndDateTime = new Date(
            Date.UTC(
                eventDate.getFullYear(),
                eventDate.getMonth(),
                eventDate.getDate(),
                endEventTime.getHours(),
                endEventTime.getMinutes(),
                endEventTime.getSeconds()
            )
        );

        // Build the updated session object with correctly formatted dates and times.
        const updatedSession = {
            session_type: "event", // default session type
            capacity: capacity.trim() ? Number(capacity) : null,
            price: price.trim() ? Number(price) : null,
            start_datetime: eventStartDateTime.toISOString(),
            end_datetime: eventEndDateTime.toISOString(),
            day_of_week: null,
            start_time: null,
            end_time: null,
            start_date: null,
            end_date: null,
            address: null // Adjust as needed or set to null if not required.
        };

        try {
            // Call updateSession with the updated session object.
            await updateSession(club_id, program_id, session_id, updatedSession, false, false);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
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
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("update_event")} />
                        </View>
                        {pricing_model === "per_session" && (
                            <>
                                <DefaultTextFieldInput
                                    placeholder={t("program_price_placeholder")}
                                    value={price}
                                    onChangeText={(text) => {
                                        setPrice(text);
                                        if (text.trim()) {
                                            setPriceError(false);
                                        }
                                    }}
                                    hasError={priceError}
                                />
                                <DefaultTextFieldInput
                                    placeholder={t("program_capacity_placeholder")}
                                    value={capacity}
                                    onChangeText={(text) => {
                                        setCapacity(text);
                                        if (text.trim()) {
                                            setCapacityError(false);
                                        }
                                    }}
                                    hasError={capacityError}
                                />
                            </>
                        )}
                        <DefaultText text={t("event_start_date")} />
                        {/* DateTimePicker for start time using the updated start_date */}
                        <DateTimePicker mode="time" value={startEventTime} onConfirm={setStartEventTime} />
                        <DefaultText text={t("event_end_date")} />
                        {/* DateTimePicker for end time using the updated end_date */}
                        <DateTimePicker mode="time" value={endEventTime} onConfirm={setEndEventTime} />
                        <DefaultText text={t("event_date")} />
                        {/* DateTimePicker for event date */}
                        <DateTimePicker
                            mode="date"
                            value={eventDate}
                            onConfirm={setEventDate}
                            minimumDate={tomorrow}
                        />
                        <DefaultButton text={t("save_session_btn")} onPress={handleUpdatePress} />
                        <Subheading text={t("delete_event")} />
                        <DefaultTextFieldInput
                            placeholder={t("session_delete_note_placeholder")}
                            value={note}
                            onChangeText={(text) => {
                                setNote(text);
                                if (text.trim()) {
                                    setNoteError(false);
                                }
                            }}
                            hasError={noteError}
                        />
                        <DefaultButton text={t("delete_session_btn")} onPress={handleDeletePress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageEvent;
