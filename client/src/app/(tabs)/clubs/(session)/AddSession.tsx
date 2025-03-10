import React, { useState, useEffect } from 'react';
import { ScrollView, View, Pressable, useColorScheme, TouchableWithoutFeedback, Platform, KeyboardAvoidingView, Keyboard } from 'react-native';
import { useRouter, useNavigation, useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { TimePickerTrigger, InlineTimePopover } from '@/src/components/picker/TimePicker';
import { DatePickerTrigger, InlineDatePopover } from '@/src/components/picker/DatePicker';
import Heading from '@/src/components/textFields/Heading';
import Dropdown from '@/src/components/dropdown/Dropdown';
import DefaultTextFieldInput from '@/src/components/textInputs/DefaultTextInput';
import OptionSwitch from '@/src/components/optionSwitch/OptionSwitch';
import DefaultText from '@/src/components/textFields/DefaultText';
import { getCountries } from '@/src/services/static/countryService';
import DefaultButton from '@/src/components/buttons/DefaultButton';
import { createSession } from '@/src/services/club/programSessionService';
import Toast from 'react-native-toast-message';
import DefaultToast from '@/src/components/defaultToast/DefaultToast';

interface Address {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
}

interface sessions {
    session_type: string;
    capacity: number | null;
    price: number | null;
    start_datetime: string | null;
    end_datetime: string | null;
    day_of_week: string | null;
    start_time: string | null;
    end_time: string | null;
    start_date: string | null;
    end_date: string | null;
    address: Address | null;
}

//! This component is somehow very slow in responing (needs sometimes more then one press to respond)
//TODO: Check why this is so slow
const AddSession = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t, i18n } = useTranslation('clubs');
    const { club_id, program_id, pricing_model } = useLocalSearchParams();

    const [price, setPrice] = useState('');
    const [priceError, setPriceError] = useState(false);
    const [capacity, setCapacity] = useState('');
    const [capacityError, setCapacityError] = useState(false);
    const [differentAddress, setDifferentAddress] = useState(false);
    const [sessionType, setSessionType] = useState("");
    const [selectedWeekday, setSelectedWeekday] = useState("");
    const [sessionTypeError, setSessionTypeError] = useState(false);

    const [country, setCountry] = useState("");
    const [street, setStreet] = useState("");
    const [city, setCity] = useState("");
    const [zip, setZip] = useState("");
    const [state, setState] = useState("");
    // Note: Address will be conditionally sent so we keep it separate
    const [address, setAddress] = useState<Address | null>(null);

    // Error states for the fields.
    const [nameError, setNameError] = useState(false);
    const [descriptionError, setDescriptionError] = useState(false);
    const [streetError, setStreetError] = useState(false);
    const [cityError, setCityError] = useState(false);
    const [zipError, setZipError] = useState(false);
    const [stateError, setStateError] = useState(false);
    const [addressError, setAddressError] = useState(false);

    // States for the two time pickers
    const [startEventTime, setStartEventTime] = useState(new Date());
    const [endEventTime, setEndEventTime] = useState(new Date());

    // State to track which TimePicker is active ("start" or "end")
    const [activeTimePicker, setActiveTimePicker] = useState<null | 'start' | 'end'>(null);
    const [timePopoverVisible, setTimePopoverVisible] = useState(false);

    // States for the DatePickers
    // Separate states for event date and course end date
    const [eventDate, setEventDate] = useState(new Date());
    const [courseEndDate, setCourseEndDate] = useState(new Date());
    // Active date picker: either 'event' or 'courseEnd'
    const [activeDatePicker, setActiveDatePicker] = useState<null | 'event' | 'courseEnd'>(null);
    const [datePopoverVisible, setDatePopoverVisible] = useState(false);

    // New state: whether the user wants to set an end_date for a course
    const [setCourseEndDateOption, setSetCourseEndDateOption] = useState(false);

    // State to hold full countries list from the API
    const [fetchedCountries, setFetchedCountries] = useState<any[]>([]);
    // State to track the selected country's ISO2 code from the dropdown
    const [selectedCountryKey, setSelectedCountryKey] = useState("");

    // Fetch the countries and store the full response in state.
    useEffect(() => {
        async function fetchCountries() {
            try {
                const data = await getCountries();
                setFetchedCountries(data.countries);
                // Optionally, set a default country if needed.
            } catch (error) {
                console.error("Error fetching countries", error);
            }
        }
        fetchCountries();
    }, []);

    // Update the country state whenever the selected country changes.
    useEffect(() => {
        if (selectedCountryKey) {
            const selected = fetchedCountries.find((c) => c.iso2 === selectedCountryKey);
            if (selected) {
                setCountry(selected.name);
            }
        }
    }, [selectedCountryKey, fetchedCountries]);

    // Build dropdown list using the current language for display.
    const dropdownOptions = fetchedCountries.map((c) => {
        const translatedName = c.translations[i18n.language] || c.name;
        return { key: c.iso2, value: translatedName };
    });

    // State for theme (light or dark)
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === 'light');
    }, [colorScheme]);
    const iconColor = isLight ? '#000000' : '#FFFFFF';

    // Handler to dismiss the screen
    const handleDismissPress = () => {
        router.dismiss();
    };

    // Handler when the time popover closes
    const handleTimePopoverClose = (time: Date) => {
        if (activeTimePicker === 'start') {
            setStartEventTime(time);
        } else if (activeTimePicker === 'end') {
            setEndEventTime(time);
        }
        setActiveTimePicker(null);
        setTimePopoverVisible(false);
    };

    // Handler when the date popover closes.
    // Updates the appropriate state based on the active date picker.
    const handleDatePopoverClose = (
        selected: Date | { startDate: Date; endDate: Date }
    ) => {
        if (selected instanceof Date) {
            if (activeDatePicker === 'event') {
                setEventDate(selected);
            } else if (activeDatePicker === 'courseEnd') {
                setCourseEndDate(selected);
            }
        }
        setActiveDatePicker(null);
        setDatePopoverVisible(false);
    };

    // Set custom header with a dismiss button
    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: 'auto', marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    const weekValues = [
        { key: 'Monday', value: t('monday') },
        { key: 'Tuesday', value: t('tuesday') },
        { key: 'Wednesday', value: t('wednesday') },
        { key: 'Thursday', value: t('thursday') },
        { key: 'Friday', value: t('friday') },
        { key: 'Saturday', value: t('saturday') },
        { key: 'Sunday', value: t('sunday') },
    ];

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minCourseEndDate = new Date(eventDate);
    minCourseEndDate.setDate(minCourseEndDate.getDate() + 1);

    const handleCreatePress = async () => {
        let errorFound = false;

        // Validate session type
        if (!sessionType.trim()) {
            setSessionTypeError(true);
            errorFound = true;
        }

        // Validate pricing_model specific fields (per_session)
        if (pricing_model === "per_session") {
            if (!price.trim()) {
                setPriceError(true);
                errorFound = true;
            }
            if (!capacity.trim()) {
                setCapacityError(true);
                errorFound = true;
            }
        }

        // Validate that start time is before end time for both event and course
        if (startEventTime >= endEventTime) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("Start time must be before end time")
            });
            errorFound = true;
        }

        // Additional validations for course session type
        if (sessionType === "course") {
            if (!selectedWeekday.trim()) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("Please select a weekday for the course")
                });
                errorFound = true;
            }
            if (setCourseEndDateOption && (new Date(courseEndDate) <= new Date(eventDate))) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("Course end date must be after the course start date")
                });
                errorFound = true;
            }
        }

        // Validate address fields if a different address is required
        if (differentAddress) {
            if (!street.trim()) {
                setStreetError(true);
                errorFound = true;
            }
            if (!zip.trim()) {
                setZipError(true);
                errorFound = true;
            }
            if (!city.trim()) {
                setCityError(true);
                errorFound = true;
            }
            if (!state.trim()) {
                setStateError(true);
                errorFound = true;
            }
            if (!country.trim()) {
                setAddressError(true);
                errorFound = true;
            }
        }

        // If any validation failed, show a generic error message and exit
        if (errorFound) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext"),
            });
            return;
        }

        try {
            const formattedStartTime = startEventTime.toISOString().split("T")[1].split(".")[0];
            const formattedEndTime = endEventTime.toISOString().split("T")[1].split(".")[0];

            // Build sessionData based on sessionType and pricing_model
            const sessionData: sessions = {
                session_type: sessionType,
                // If pricing_model is per_session, use provided values, else set to null
                capacity: pricing_model === "per_session" ? parseInt(capacity) : null,
                price: pricing_model === "per_session" ? parseInt(price) : null,
                // For events, send start_datetime and end_datetime, otherwise null
                start_datetime: sessionType === "event" ? startEventTime.toISOString() : null,
                end_datetime: sessionType === "event" ? endEventTime.toISOString() : null,
                // For courses, send day_of_week, start_time, end_time, start_date and optionally end_date
                day_of_week: sessionType === "course" ? selectedWeekday : null,
                start_time: sessionType === "course" ? formattedStartTime : null,
                end_time: sessionType === "course" ? formattedEndTime : null,
                start_date: sessionType === "course" ? eventDate.toISOString().split("T")[0] : null,
                end_date: sessionType === "course"
                    ? (setCourseEndDateOption ? courseEndDate.toISOString().split("T")[0] : null)
                    : null,
                // Send the address if differentAddress is true, otherwise null
                address: differentAddress
                    ? {
                        street,
                        postal_code: zip,
                        city,
                        state,
                        country,
                    }
                    : null,
            };
            await createSession(club_id, program_id, sessionData);
            router.back();
        } catch (error) {
            console.error("Error during createSession call:", error);
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
            return;
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{ flex: 1 }} // Ensure the KeyboardAvoidingView fills the screen
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View style={{ flex: 1 }} pointerEvents="box-none">
                    <ScrollView
                        scrollEnabled={!(timePopoverVisible || datePopoverVisible)}
                        keyboardShouldPersistTaps="always"
                        contentContainerStyle={{ flexGrow: 1, paddingBottom: 100 }}
                        style={{ flex: 1 }}
                        className='bg-light_primary dark:bg-dark_primary'
                    >
                        <View className='justify-center items-center'>
                            <View className='py-4'>
                                <Heading text={t('create_session_header')} />
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
                            <Dropdown
                                setSelected={(selected) => {
                                    setSessionType(selected);
                                    setSessionTypeError(false);
                                }}
                                values={[
                                    { key: "course", value: t("course") },
                                    { key: "event", value: t("event") }
                                ]}
                                placeholder={t("selectSessionType_placeholder")}
                                save="key"
                            />
                            <DefaultText text={t("event_start_date")} />
                            {/* Time picker for event start time */}
                            <TimePickerTrigger
                                selectedTime={startEventTime}
                                onPress={() => {
                                    setActiveTimePicker('start');
                                    setTimePopoverVisible(true);
                                }}
                            />
                            <DefaultText text={t("event_end_date")} />
                            {/* Time picker for event end time */}
                            <TimePickerTrigger
                                selectedTime={endEventTime}
                                onPress={() => {
                                    setActiveTimePicker('end');
                                    setTimePopoverVisible(true);
                                }}
                            />
                            {sessionType === "course" ? (
                                <DefaultText text={t("course_start_date")} />
                            ) : (
                                <DefaultText text={t("event_date")} />
                            )}
                            {/* Date picker trigger for the event date */}
                            <DatePickerTrigger
                                selectedDate={eventDate}
                                onPress={() => {
                                    setActiveDatePicker('event');
                                    setDatePopoverVisible(true);
                                }}
                            />
                            {sessionType === "course" && (
                                <>
                                    {/* OptionSwitch to decide if an end_date should be set */}
                                    <OptionSwitch
                                        title={t("set_course_end_date")}
                                        texts={[t("enable_course_end_date")]}
                                        iconNames={["calendar-today"]}
                                        values={[setCourseEndDateOption]}
                                        onValueChanges={[
                                            () => setSetCourseEndDateOption(prev => !prev)
                                        ]}
                                    />
                                    {setCourseEndDateOption && (
                                        <>
                                            <DefaultText text={t("course_end_date")} />
                                            {/* Date picker trigger for the course end date */}
                                            <DatePickerTrigger
                                                selectedDate={courseEndDate}
                                                onPress={() => {
                                                    setActiveDatePicker('courseEnd');
                                                    setDatePopoverVisible(true);
                                                }}
                                            />
                                        </>
                                    )}
                                    <DefaultText text={t("course_weekday")} />
                                    <Dropdown
                                        setSelected={(selected) => {
                                            setSelectedWeekday(selected);
                                        }}
                                        values={weekValues}
                                        placeholder={t("selectWeekday_placeholder")}
                                        save="key"
                                    />
                                </>
                            )}
                            <OptionSwitch
                                title={t("different_address")}
                                texts={[t("different_address_enabled")]}
                                iconNames={["person"]}
                                values={[differentAddress]}
                                onValueChanges={[
                                    () => setDifferentAddress(prev => !prev)
                                ]}
                            />
                            {differentAddress && (
                                <>
                                    <DefaultTextFieldInput
                                        placeholder={t("street_placeholder")}
                                        value={street}
                                        onChangeText={(text) => {
                                            setStreet(text);
                                            if (text.trim()) {
                                                setStreetError(false);
                                            }
                                        }}
                                        hasError={streetError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("zip_placeholder")}
                                        value={zip}
                                        onChangeText={(text) => {
                                            setZip(text);
                                            if (text.trim()) {
                                                setZipError(false);
                                            }
                                        }}
                                        hasError={zipError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("city_placeholder")}
                                        value={city}
                                        onChangeText={(text) => {
                                            setCity(text);
                                            if (text.trim()) {
                                                setCityError(false);
                                            }
                                        }}
                                        hasError={cityError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("state_placeholder")}
                                        value={state}
                                        onChangeText={(text) => {
                                            setState(text);
                                            if (text.trim()) {
                                                setStateError(false);
                                            }
                                        }}
                                        hasError={stateError}
                                    />
                                    <Dropdown
                                        search={true}
                                        setSelected={setSelectedCountryKey}
                                        values={dropdownOptions}
                                        placeholder={t("country_placeholder")}
                                        save="key"
                                    />
                                </>
                            )}
                            <View className='justify-center items-center w-full pb-4'>
                                <DefaultButton text={t("create_session_btn")} onPress={handleCreatePress} />
                            </View>
                        </View>
                    </ScrollView>
                    {/* Render a single InlineTimePopover which updates based on the activeTimePicker */}
                    {timePopoverVisible && (
                        <InlineTimePopover onClose={handleTimePopoverClose} />
                    )}
                    {/* Render a single InlineDatePopover which updates based on the activeDatePicker */}
                    {datePopoverVisible && (
                        <InlineDatePopover
                            minimumDate={activeDatePicker === 'courseEnd' ? minCourseEndDate : tomorrow}
                            onClose={handleDatePopoverClose}
                        />
                    )}
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddSession;
