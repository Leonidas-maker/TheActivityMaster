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

interface Address {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
}

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

    const [country, setCountry] = useState("");
    const [street, setStreet] = useState("");
    const [city, setCity] = useState("");
    const [zip, setZip] = useState("");
    const [state, setState] = useState("");
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

    // State to hold full countries list from the API
    const [fetchedCountries, setFetchedCountries] = useState<any[]>([]);
    // State to track the selected country's ISO2 code from the dropdown
    const [selectedCountryKey, setSelectedCountryKey] = useState("");

    // Fetch the countries and store the full response in state
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
        { key: 'mon', value: t('monday') },
        { key: 'tue', value: t('tuesday') },
        { key: 'wed', value: t('wednesday') },
        { key: 'thu', value: t('thursday') },
        { key: 'fri', value: t('friday') },
        { key: 'sat', value: t('saturday') },
        { key: 'sun', value: t('sunday') },
    ];

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minCourseEndDate = new Date(eventDate);
    minCourseEndDate.setDate(minCourseEndDate.getDate() + 1);

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{ flex: 1 }} // Ensure the KeyboardAvoidingView fills the screen
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View style={{ flex: 1 }}> {/* Add flex:1 here */}
                    <ScrollView
                        scrollEnabled={!(timePopoverVisible || datePopoverVisible)}
                        keyboardShouldPersistTaps="always"
                        contentContainerStyle={{ flexGrow: 1, paddingBottom: 20 }}
                        style={{ flex: 1 }} // Optionally add flex:1 for the ScrollView itself
                        className="bg-light_primary dark:bg-dark_primary"
                    >
                        <View className='justify-center items-center'>
                            <View className='py-4'>
                                <Heading text={t('createClub')} />
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
                                <>
                                    <DefaultText text={t("course_start_time")} />
                                </>
                            ) : (
                                <>
                                    <DefaultText text={t("event_date")} />
                                </>
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
                                    <View className='w-full justify-center items-center'>
                                        <DefaultText text={t("course_end_time")} />
                                        {/* Date picker trigger for the course end date */}
                                        <DatePickerTrigger
                                            selectedDate={courseEndDate}
                                            onPress={() => {
                                                setActiveDatePicker('courseEnd');
                                                setDatePopoverVisible(true);
                                            }}
                                        />
                                        <DefaultText text={t("course_weekday")} />
                                        <Dropdown
                                            setSelected={(selected) => {
                                                setSelectedWeekday(selected);
                                            }}
                                            values={weekValues}
                                            placeholder={t("selectWeekday_placeholder")}
                                            save="key"
                                        />
                                    </View>
                                </>
                            )}
                            <OptionSwitch
                                title={t("membership_required")}
                                texts={[t("enable_membership")]}
                                iconNames={["person"]}
                                values={[differentAddress]}
                                onValueChanges={[
                                    () => setDifferentAddress((prev) => !prev)
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
                                <DefaultButton />
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
        </KeyboardAvoidingView>
    );
};

export default AddSession;
