import React, { useState, useEffect, useRef, useCallback } from "react";
import {
    View,
    ScrollView,
    KeyboardAvoidingView,
    Platform,
    Keyboard,
    TouchableWithoutFeedback,
    Animated,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useFocusEffect } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { register } from "@/src/services/user/userService";

// Custom components
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import SecondaryButton from "@/src/components/buttons/SecondaryButton";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
// Import the Dropdown component for country selection
import Dropdown from "@/src/components/dropdown/Dropdown";
import StepProgressBar from "@/src/components/stepProgressBar/StepProgressBar";
import Subheading from "@/src/components/textFields/Subheading";
import { getCountries } from "@/src/services/static/countryService";
import { createClub } from "@/src/services/club/clubService";

interface address {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
};

const ClubCreate = () => {
    // Destructure i18n along with t to get the current language
    const { t, i18n } = useTranslation("clubs");
    const router = useRouter();

    // Step state and field states.
    const [currentStep, setCurrentStep] = useState(0);
    const totalSteps = 2;

    // Step 1: Name and Description.
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    // Step 2: Address Information.
    const [country, setCountry] = useState("");
    const [street, setStreet] = useState("");
    const [city, setCity] = useState("");
    const [zip, setZip] = useState("");
    const [state, setState] = useState("");
    const [address, setAddress] = useState<address | null>(null);

    // Error states for the fields.
    const [nameError, setNameError] = useState(false);
    const [descriptionError, setDescriptionError] = useState(false);
    const [streetError, setStreetError] = useState(false);
    const [cityError, setCityError] = useState(false);
    const [zipError, setZipError] = useState(false);
    const [stateError, setStateError] = useState(false);
    const [addressError, setAddressError] = useState(false);

    // Animated value for step content transitions.
    const fieldAnim = useRef(new Animated.Value(0)).current;
    const isInitialMount = useRef(true);

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
                // Optionally, set a default selected country based on your logic.
                // For instance, if the default "Germany" is available, set it.
                const defaultCountry = data.countries.find(
                    (c: any) => c.name === "Germany"
                );
                //if (defaultCountry) {
                //    setSelectedCountryKey(defaultCountry.iso2);
                //    setCountry(defaultCountry.name); // set default name for registration
                //}
            } catch (error) {
                console.error("Error fetching countries", error);
            }
        }
        fetchCountries();
    }, []);

    // Update the country state (default name) whenever the selected country changes.
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
        // Use the translation for the current language if available; otherwise fallback to the default name.
        const translatedName = c.translations[i18n.language] || c.name;
        return { key: c.iso2, value: translatedName };
    });

    useEffect(() => {
        if (currentStep === 0 && isInitialMount.current) {
            fieldAnim.setValue(1);
            isInitialMount.current = false;
        } else {
            fieldAnim.setValue(0);
            Animated.timing(fieldAnim, {
                toValue: 1,
                duration: 300,
                useNativeDriver: true,
            }).start();
        }
    }, [currentStep, fieldAnim]);

    const animatedStyle = {
        opacity: fieldAnim,
        transform: [
            {
                translateY: fieldAnim.interpolate({
                    inputRange: [0, 1],
                    outputRange: [20, 0],
                }),
            },
        ],
    };

    const getStepProgress = (): number => {
        switch (currentStep) {
            case 0: {
                const totalFields = 2;
                const filled =
                    (name.trim() !== "" ? 1 : 0) +
                    (description.trim() !== "" ? 1 : 0)
                return filled / totalFields;
            }
            case 1: {
                const totalFields = 5;
                const filled =
                    (country.trim() !== "" ? 1 : 0) +
                    (street.trim() !== "" ? 1 : 0) +
                    (city.trim() !== "" ? 1 : 0) +
                    (zip.trim() !== "" ? 1 : 0) +
                    (state.trim() !== "" ? 1 : 0);
                return filled / totalFields;
            }
            default:
                return 0;
        }
    };

    const stepProgress = getStepProgress();

    const handleNext = () => {
        // Validate inputs for step 0 (Email and Username).
        if (currentStep === 0) {
            const isNameEmpty = !name.trim();
            const isDescriptionEmpty = !description.trim();

            if (isNameEmpty || isDescriptionEmpty) {
                if (isNameEmpty) setNameError(true);
                if (isDescriptionEmpty) setDescriptionError(true);

                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
                return;
            }
        }

        // Move to the next step if not at the last step.
        if (currentStep < totalSteps - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleSubmit = async () => {
        const isCountryEmpty = !country.trim();
        const isStateEmpty = !state.trim();
        const isStreetEmpty = !street.trim();
        const isZipEmpty = !zip.trim();
        const isCityEmpty = !city.trim();

        if (isCountryEmpty || isStateEmpty || isStreetEmpty || isZipEmpty || isCityEmpty) {
            if (isCountryEmpty) setAddressError(true);
            if (isStateEmpty) setStateError(true);
            if (isStreetEmpty) setStreetError(true);
            if (isZipEmpty) setZipError(true);
            if (isCityEmpty) setCityError(true);

            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext"),
            });
            return;
        }

        const address = {
            street,
            postal_code: zip,
            city,
            state,
            country,
        };
        try {
            await createClub(
                name,
                description,
                address
            );

            while (router.canGoBack()) {
                router.back();
            }
            router.navigate("/(tabs)/overview")
        } catch (error: any) {
            console.error("Club creation error:", error);
            Toast.show({
                type: "error",
                text1: t("clubError_text"),
                text2: t("clubError_subtext"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView
                    className="h-screen bg-light_primary dark:bg-dark_primary"
                    keyboardShouldPersistTaps="handled"
                    contentContainerStyle={{ flexGrow: 1 }}
                >
                    <View className="flex-1 px-4 py-6">
                        <StepProgressBar
                            currentStep={currentStep}
                            totalSteps={totalSteps}
                            fieldProgress={stepProgress}
                            onStepPress={(step) => {
                                if (step <= currentStep) {
                                    setCurrentStep(step);
                                }
                            }}
                        />

                        <Animated.View style={animatedStyle} className="w-full">
                            {currentStep === 0 && (
                                <View className="w-full items-center">
                                    <Subheading text={t("creation_step1_title")} />
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
                                </View>
                            )}
                            {currentStep === 1 && (
                                <View className="w-full items-center">
                                    <Subheading text={t("creation_step2_title")} />
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
                                </View>
                            )}
                        </Animated.View>

                        <View className="w-full items-center mt-6">
                            {currentStep < totalSteps - 1 ? (
                                <DefaultButton text={t("next_button")} onPress={handleNext} />
                            ) : (
                                <DefaultButton text={t("club_create_button")} onPress={handleSubmit} />
                            )}
                            {currentStep > 0 && <SecondaryButton text={t("back_button")} onPress={handleBack} />}
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ClubCreate;
