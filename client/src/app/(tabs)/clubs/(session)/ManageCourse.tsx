import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
    ScrollView,
    View,
    Pressable,
    useColorScheme,
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
import Icon from "react-native-vector-icons/MaterialIcons";
import DateTimePicker from "@/src/components/picker/DateTimePicker";
import Subheading from "@/src/components/textFields/Subheading";
import { updateSession, deleteSession } from "@/src/services/club/programSessionService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Dropdown from "@/src/components/dropdown/Dropdown";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";

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

const ManageCourse = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const {
        club_id,
        program_id,
        session_id,
        pricing_model,
        day_of_week,
        start_time,
        end_time,
        start_date,
        end_date,
        capacity_event,
        price_event
    } = useLocalSearchParams();

    // Extract query parameter values
    const startDateStr = getParamValue(start_date);
    const startTimeStr = getParamValue(start_time);
    const endTimeStr = getParamValue(end_time);
    const endDateParam = getParamValue(end_date);
    const initialWeekday = getParamValue(day_of_week);

    // Build initial date/time values from the provided params.
    const initialStartDateTime =
        startDateStr && startTimeStr && startDateStr !== "undefined" && startTimeStr !== "undefined"
            ? new Date(`${startDateStr}T${startTimeStr}`)
            : new Date();
    const initialEndDateTime =
        startDateStr && endTimeStr && startDateStr !== "undefined" && endTimeStr !== "undefined"
            ? new Date(`${startDateStr}T${endTimeStr}`)
            : new Date();
    const initialEventDate = startDateStr && startDateStr !== "undefined" ? new Date(startDateStr) : new Date();

    // If the third last value (end_date) is provided (not "undefined"), then use it for the course end date.
    const initialCourseEndDate =
        endDateParam && endDateParam !== "undefined" ? new Date(endDateParam) : new Date();
    const initialCourseEndDateOption = endDateParam && endDateParam !== "undefined" ? true : false;

    // Store initial values for later change comparison.
    const initialPrice = getParamValue(price_event);
    const initialCapacity = getParamValue(capacity_event);

    // States for price, capacity, note and weekday
    const [price, setPrice] = useState(initialPrice);
    const [priceError, setPriceError] = useState(false);
    const [capacity, setCapacity] = useState(initialCapacity);
    const [capacityError, setCapacityError] = useState(false);
    const [note, setNote] = useState("");
    const [noteError, setNoteError] = useState(false);
    const [selectedWeekday, setSelectedWeekday] = useState(initialWeekday);

    // States for the time pickers using the combined date and time values.
    const [startCourseTime, setStartCourseTime] = useState(initialStartDateTime);
    const [endCourseTime, setEndCourseTime] = useState(initialEndDateTime); // updated variable name

    // States for the DatePicker using the event date.
    const [courseDate, setCourseDate] = useState(initialEventDate);
    const [courseEndDate, setCourseEndDate] = useState(initialCourseEndDate);
    const [courseEndDateOption, setCourseEndDateOption] = useState(initialCourseEndDateOption);

    // Update date/time state if query parameters change
    useEffect(() => {
        if (startDateStr && startTimeStr && startDateStr !== "undefined" && startTimeStr !== "undefined") {
            const newStart = new Date(`${startDateStr}T${startTimeStr}`);
            setStartCourseTime(newStart);
            // Also update the event date if needed
            setCourseDate(new Date(startDateStr));
        }
        if (startDateStr && endTimeStr && startDateStr !== "undefined" && endTimeStr !== "undefined") {
            setEndCourseTime(new Date(`${startDateStr}T${endTimeStr}`));
        }
        if (endDateParam && endDateParam !== "undefined") {
            setCourseEndDate(new Date(endDateParam));
            setCourseEndDateOption(true);
        }
    }, [startDateStr, startTimeStr, endTimeStr, endDateParam]);

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
    // For course end date, at least one day after the selected start date.
    const minCourseEndDate = useMemo(() => {
        const date = new Date(courseDate);
        date.setDate(date.getDate() + 1);
        return date;
    }, [courseDate]);

    // Helper function to format a Date object into a time string using local time (e.g., "13:03:15.719Z")
    const formatLocalTime = (date: any) => {
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        const seconds = date.getSeconds().toString().padStart(2, "0");
        const milliseconds = date.getMilliseconds().toString().padStart(3, "0");
        return `${hours}:${minutes}:${seconds}.${milliseconds}Z`;
    };

    // Handler for update button with change checking, field validation, and proper local time formatting.
    const handleUpdatePress = async () => {
        // Validate required fields when pricing model is per session.
        if (pricing_model === "per_session") {
            if (!price.trim()) {
                setPriceError(true);
            }
            if (!capacity.trim()) {
                setCapacityError(true);
            }

            if (!price.trim() || !capacity.trim()) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
                return;
            }
        }

        // Check if any of the key fields have changed compared to the initial values,
        // including whether the end date option (courseEndDateOption) has been toggled.
        if (
            price === initialPrice &&
            capacity === initialCapacity &&
            startCourseTime.getTime() === initialStartDateTime.getTime() &&
            endCourseTime.getTime() === initialEndDateTime.getTime() &&
            courseDate.toISOString().split("T")[0] === initialEventDate.toISOString().split("T")[0] &&
            selectedWeekday === initialWeekday &&
            courseEndDateOption === initialCourseEndDateOption &&
            (
                !courseEndDateOption ||
                (courseEndDate.toISOString().split("T")[0] === initialCourseEndDate.toISOString().split("T")[0])
            )
        ) {
            Toast.show({
                type: "info",
                text1: t("noChangesMade"),
                text2: t("noChangesDescription"),
            });
            return;
        }

        // Use the custom function to format the local time for start_time and end_time.
        const startTimeOnly = formatLocalTime(startCourseTime);
        const endTimeOnly = formatLocalTime(endCourseTime);

        // Build the updated session object.
        const updatedSession = {
            session_type: "course", // set session type to "course"
            capacity: capacity.trim() ? Number(capacity) : null,
            price: price.trim() ? Number(price) : null,
            start_datetime: null, // not used for courses
            end_datetime: null,   // not used for courses
            day_of_week: selectedWeekday,
            start_time: startTimeOnly,
            end_time: endTimeOnly,
            start_date: courseDate.toISOString().split("T")[0],
            end_date: courseEndDateOption
                ? courseEndDate.toISOString().split("T")[0] // use formatted end date if enabled
                : null, // set to null if disabled
            address: null, // adjust as needed
        };

        const null_end_date = courseEndDateOption ? false : true;

        try {
            // Call updateSession with the updated session object.
            await updateSession(club_id, program_id, session_id, updatedSession, null_end_date, false);
            for (let i = 0; i < 2; i++) {
                router.back()
            }
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
        }
    };

    // Handler for delete button with validation of the deletion note.
    const handleDeletePress = async () => {
        Alert.alert(
            t("delete_course"),
            t("delete_course_confirmation"),
            [
                {
                    text: t("cancel_btn"),
                    style: "cancel",
                },
                {
                    text: t("confirm_btn"),
                    onPress: handleDelete,
                },
            ]
        );
    };

    // Helper function to handle the deletion of the session.
    const handleDelete = async () => {
        try {
            // Call deleteSession with the note.
            await deleteSession(club_id, program_id, session_id, note);
            for (let i = 0; i < 2; i++) {
                router.back()
            }
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
        }
    };

    // Weekday options for courses
    const weekValues = [
        { key: 'Monday', value: t('monday') },
        { key: 'Tuesday', value: t('tuesday') },
        { key: 'Wednesday', value: t('wednesday') },
        { key: 'Thursday', value: t('thursday') },
        { key: 'Friday', value: t('friday') },
        { key: 'Saturday', value: t('saturday') },
        { key: 'Sunday', value: t('sunday') },
    ];

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("update_course")} />
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
                        {/* DateTimePicker for start time using the combined date and time */}
                        <DateTimePicker mode="time" value={startCourseTime} onConfirm={setStartCourseTime} />
                        <DefaultText text={t("event_end_date")} />
                        {/* DateTimePicker for end time using the combined date and time */}
                        <DateTimePicker mode="time" value={endCourseTime} onConfirm={setEndCourseTime} />
                        <DefaultText text={t("event_date")} />
                        {/* DateTimePicker for event date */}
                        <DateTimePicker
                            mode="date"
                            value={courseDate}
                            onConfirm={setCourseDate}
                            minimumDate={tomorrow}
                        />
                        <OptionSwitch
                            title={t("set_course_end_date")}
                            texts={[t("enable_course_end_date")]}
                            iconNames={["calendar-today"]}
                            values={[courseEndDateOption]}
                            onValueChanges={[() => setCourseEndDateOption(prev => !prev)]}
                        />
                        {courseEndDateOption && (
                            <>
                                <DefaultText text={t("course_end_date")} />
                                <DateTimePicker
                                    mode="date"
                                    value={courseEndDate}
                                    onConfirm={setCourseEndDate}
                                    minimumDate={minCourseEndDate}
                                />
                            </>
                        )}
                        <DefaultText text={t("course_weekday")} />
                        <Dropdown
                            setSelected={setSelectedWeekday}
                            values={weekValues}
                            placeholder={t("selectWeekday_placeholder")}
                            save="key"
                            defaultOption={weekValues.find(option => option.key === selectedWeekday)}
                        />
                        <DefaultButton text={t("save_course_btn")} onPress={handleUpdatePress} />
                        <Subheading text={t("delete_course")} />
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
                        <View className="w-full items-center mb-6">
                            <DefaultButton text={t("delete_course_btn")} onPress={handleDeletePress} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageCourse;
