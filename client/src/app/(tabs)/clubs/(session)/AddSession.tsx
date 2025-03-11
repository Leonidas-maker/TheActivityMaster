import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ScrollView, View, Pressable, useColorScheme, TouchableWithoutFeedback, Platform, KeyboardAvoidingView, Keyboard } from 'react-native';
import { useRouter, useNavigation, useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialIcons';
import DateTimePicker from '@/src/components/picker/DateTimePicker';
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

interface SessionData {
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

//! On iOS this screen is very slow to respond to clicks, I am not sure why
//TODO: Look into why this screen is slow to respond to clicks on iOS
const AddSession = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t, i18n } = useTranslation('clubs');
    const { club_id, program_id, pricing_model } = useLocalSearchParams();

    // Input state variables
    const [price, setPrice] = useState('');
    const [capacity, setCapacity] = useState('');
    const [sessionType, setSessionType] = useState('');
    const [selectedWeekday, setSelectedWeekday] = useState('');
    const [differentAddress, setDifferentAddress] = useState(false);
    const [country, setCountry] = useState('');
    const [street, setStreet] = useState('');
    const [city, setCity] = useState('');
    const [zip, setZip] = useState('');
    const [stateVal, setStateVal] = useState(''); // renamed from "state" to avoid confusion

    // Error state variables
    const [priceError, setPriceError] = useState(false);
    const [capacityError, setCapacityError] = useState(false);
    const [sessionTypeError, setSessionTypeError] = useState(false);
    const [streetError, setStreetError] = useState(false);
    const [cityError, setCityError] = useState(false);
    const [zipError, setZipError] = useState(false);
    const [stateError, setStateError] = useState(false);
    const [addressError, setAddressError] = useState(false);

    // Date and time state variables
    const [startEventTime, setStartEventTime] = useState(new Date());
    const [endEventTime, setEndEventTime] = useState(new Date());
    const [eventDate, setEventDate] = useState(new Date());
    const [courseEndDate, setCourseEndDate] = useState(new Date());
    const [setCourseEndDateOption, setSetCourseEndDateOption] = useState(false);

    // Countries data
    const [fetchedCountries, setFetchedCountries] = useState<any[]>([]);
    const [selectedCountryKey, setSelectedCountryKey] = useState('');

    // Theme state
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === 'light');
    }, [colorScheme]);
    const iconColor = isLight ? '#000000' : '#FFFFFF';

    // Fetch countries on mount
    useEffect(() => {
        async function fetchCountries() {
            try {
                const data = await getCountries();
                setFetchedCountries(data.countries);
            } catch (error) {
                console.error("Error fetching countries", error);
            }
        }
        fetchCountries();
    }, []);

    // Update country when selectedCountryKey changes
    useEffect(() => {
        if (selectedCountryKey) {
            const selected = fetchedCountries.find((c) => c.iso2 === selectedCountryKey);
            if (selected) {
                setCountry(selected.name);
            }
        }
    }, [selectedCountryKey, fetchedCountries]);

    // Memoize dropdown options for countries
    const dropdownOptions = useMemo(
        () =>
            fetchedCountries.map((c) => {
                const translatedName = c.translations[i18n.language] || c.name;
                return { key: c.iso2, value: translatedName };
            }),
        [fetchedCountries, i18n.language]
    );

    // Calculate minimum dates:
    // Tomorrow for the start date.
    const tomorrow = useMemo(() => {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        return date;
    }, []);
    // For course end date, at least one day after the selected start date.
    const minCourseEndDate = useMemo(() => {
        const date = new Date(eventDate);
        date.setDate(date.getDate() + 1);
        return date;
    }, [eventDate]);

    // Generic handler for text input changes that resets error if text is non-empty
    const createTextChangeHandler = (
        setter: React.Dispatch<React.SetStateAction<string>>,
        errorSetter: React.Dispatch<React.SetStateAction<boolean>>
    ) => (text: string) => {
        setter(text);
        if (text.trim()) {
            errorSetter(false);
        }
    };

    // Dismiss handler wrapped with useCallback
    const handleDismissPress = useCallback(() => {
        router.dismiss();
    }, [router]);

    // Set custom header with dismiss button
    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon name="close" size={30} color={iconColor} style={{ marginLeft: 'auto', marginRight: 15 }} />
                </Pressable>
            ),
        });
    }, [navigation, iconColor, handleDismissPress]);

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

    // Validate all input fields; returns true if any error is found
    const validateInputs = () => {
        let errorFound = false;

        if (!sessionType.trim()) {
            setSessionTypeError(true);
            errorFound = true;
        }

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

        if (startEventTime >= endEventTime) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("Start time must be before end time"),
            });
            errorFound = true;
        }

        if (sessionType === "course") {
            if (!selectedWeekday.trim()) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("Please select a weekday for the course"),
                });
                errorFound = true;
            }
            if (setCourseEndDateOption && new Date(courseEndDate) <= new Date(eventDate)) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("Course end date must be after the course start date"),
                });
                errorFound = true;
            }
        }

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
            if (!stateVal.trim()) {
                setStateError(true);
                errorFound = true;
            }
            if (!country.trim()) {
                setAddressError(true);
                errorFound = true;
            }
        }

        if (errorFound) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext"),
            });
        }

        return errorFound;
    };

    // Build session data for the API request
    const buildSessionData = (): SessionData => {
        const formattedStartTime = startEventTime.toISOString().split("T")[1].split(".")[0];
        const formattedEndTime = endEventTime.toISOString().split("T")[1].split(".")[0];

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

        return {
            session_type: sessionType,
            capacity: pricing_model === "per_session" ? parseInt(capacity) : null,
            price: pricing_model === "per_session" ? parseInt(price) : null,
            start_datetime: sessionType === "event" ? eventStartDateTime.toISOString() : null,
            end_datetime: sessionType === "event" ? eventEndDateTime.toISOString() : null,
            day_of_week: sessionType === "course" ? selectedWeekday : null,
            start_time: sessionType === "course" ? formattedStartTime : null,
            end_time: sessionType === "course" ? formattedEndTime : null,
            start_date: sessionType === "course" ? eventDate.toISOString().split("T")[0] : null,
            end_date:
                sessionType === "course"
                    ? setCourseEndDateOption
                        ? courseEndDate.toISOString().split("T")[0]
                        : null
                    : null,
            address: differentAddress ? { street, postal_code: zip, city, state: stateVal, country } : null,
        };
    };

    // Handle session creation
    const handleCreatePress = async () => {
        if (validateInputs()) return;

        try {
            const sessionData = buildSessionData();
            await createSession(club_id, program_id, sessionData);
            router.back();
        } catch (error) {
            console.error("Error during createSession call:", error);
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{ flex: 1 }}>
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View style={{ flex: 1 }} pointerEvents="box-none">
                    <ScrollView
                        scrollEnabled
                        keyboardShouldPersistTaps="always"
                        contentContainerStyle={{ flexGrow: 1, paddingBottom: 100 }}
                        style={{ flex: 1 }}
                        className="bg-light_primary dark:bg-dark_primary"
                    >
                        <View className="justify-center items-center">
                            <View className="py-4">
                                <Heading text={t('create_session_header')} />
                            </View>
                            {pricing_model === "per_session" && (
                                <>
                                    <DefaultTextFieldInput
                                        placeholder={t("program_price_placeholder")}
                                        value={price}
                                        onChangeText={createTextChangeHandler(setPrice, setPriceError)}
                                        hasError={priceError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("program_capacity_placeholder")}
                                        value={capacity}
                                        onChangeText={createTextChangeHandler(setCapacity, setCapacityError)}
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
                                    { key: "event", value: t("event") },
                                ]}
                                placeholder={t("selectSessionType_placeholder")}
                                save="key"
                            />
                            <View className='w-full justify-center items-center'>
                                <DefaultText text={t("event_start_date")} />
                                <DateTimePicker mode="time" value={startEventTime} onConfirm={setStartEventTime} />
                                <DefaultText text={t("event_end_date")} />
                                <DateTimePicker mode="time" value={endEventTime} onConfirm={setEndEventTime} />
                                <DefaultText text={sessionType === "course" ? t("course_start_date") : t("event_date")} />
                                <DateTimePicker
                                    mode="date"
                                    value={eventDate}
                                    onConfirm={setEventDate}
                                    minimumDate={tomorrow}
                                />
                            </View>
                            {sessionType === "course" && (
                                <>
                                    <OptionSwitch
                                        title={t("set_course_end_date")}
                                        texts={[t("enable_course_end_date")]}
                                        iconNames={["calendar-today"]}
                                        values={[setCourseEndDateOption]}
                                        onValueChanges={[() => setSetCourseEndDateOption((prev) => !prev)]}
                                    />
                                    {setCourseEndDateOption && (
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
                                    />
                                </>
                            )}
                            <OptionSwitch
                                title={t("different_address")}
                                texts={[t("different_address_enabled")]}
                                iconNames={["person"]}
                                values={[differentAddress]}
                                onValueChanges={[() => setDifferentAddress((prev) => !prev)]}
                            />
                            {differentAddress && (
                                <>
                                    <DefaultTextFieldInput
                                        placeholder={t("street_placeholder")}
                                        value={street}
                                        onChangeText={createTextChangeHandler(setStreet, setStreetError)}
                                        hasError={streetError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("zip_placeholder")}
                                        value={zip}
                                        onChangeText={createTextChangeHandler(setZip, setZipError)}
                                        hasError={zipError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("city_placeholder")}
                                        value={city}
                                        onChangeText={createTextChangeHandler(setCity, setCityError)}
                                        hasError={cityError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("state_placeholder")}
                                        value={stateVal}
                                        onChangeText={createTextChangeHandler(setStateVal, setStateError)}
                                        hasError={stateError}
                                    />
                                    <Dropdown
                                        search
                                        setSelected={setSelectedCountryKey}
                                        values={dropdownOptions}
                                        placeholder={t("country_placeholder")}
                                        save="key"
                                    />
                                </>
                            )}
                            <View className="justify-center items-center w-full pb-4">
                                <DefaultButton text={t("create_session_btn")} onPress={handleCreatePress} />
                            </View>
                        </View>
                    </ScrollView>
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddSession;
