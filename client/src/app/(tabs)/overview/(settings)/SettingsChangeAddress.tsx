import React, { useState, useEffect } from "react";
import {
    View,
    KeyboardAvoidingView,
    Platform,
    Keyboard,
    TouchableWithoutFeedback,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import { changeAddress, getUserData } from "@/src/services/user/userService";
import { getCountries } from "@/src/services/static/countryService";

// Import the Dropdown component
import Dropdown from "@/src/components/dropdown/Dropdown";

const SettingsChangeAddress = () => {
    const router = useRouter();
    const { t, i18n } = useTranslation("settings");

    // Initial user address values
    const [initialStreet, setInitialStreet] = useState("");
    const [initialZipCode, setInitialZipCode] = useState("");
    const [initialCity, setInitialCity] = useState("");
    const [initialState, setInitialState] = useState("");
    const [initialCountry, setInitialCountry] = useState("");

    // Editable address fields
    const [street, setStreet] = useState("");
    const [zipCode, setZipCode] = useState("");
    const [city, setCity] = useState("");
    const [state, setState] = useState("");
    // country holds the default country name to send to the backend
    const [country, setCountry] = useState("");

    // Error states
    const [streetError, setStreetError] = useState(false);
    const [zipCodeError, setZipCodeError] = useState(false);
    const [cityError, setCityError] = useState(false);
    const [stateError, setStateError] = useState(false);
    const [countryError, setCountryError] = useState(false);

    // State to hold full list of countries fetched from the API
    const [fetchedCountries, setFetchedCountries] = useState<any[]>([]);
    // Track the selected country's ISO2 code from the dropdown
    const [selectedCountryKey, setSelectedCountryKey] = useState("");

    // Fetch user data on mount
    useEffect(() => {
        async function fetchUserData() {
            const userData = await getUserData();
            setInitialStreet(userData.address.street);
            setInitialZipCode(userData.address.postal_code);
            setInitialCity(userData.address.city);
            setInitialState(userData.address.state);
            setInitialCountry(userData.address.country);
            setStreet(userData.address.street);
            setZipCode(userData.address.postal_code);
            setCity(userData.address.city);
            setState(userData.address.state);
            setCountry(userData.address.country);
        }
        fetchUserData();
    }, []);

    // Fetch countries list. When initialCountry is set, try to match it
    useEffect(() => {
        async function fetchCountries() {
            try {
                const data = await getCountries();
                setFetchedCountries(data.countries);
                // If initialCountry is set, find its matching ISO2 code
                if (initialCountry) {
                    const defaultCountry = data.countries.find(
                        (c: any) => c.name === initialCountry
                    );
                    if (defaultCountry) {
                        setSelectedCountryKey(defaultCountry.iso2);
                    }
                }
            } catch (error) {
                console.error("Error fetching countries", error);
            }
        }
        fetchCountries();
    }, [initialCountry]);

    // When the selected country changes, update the 'country' state with the default name
    useEffect(() => {
        if (selectedCountryKey) {
            const selected = fetchedCountries.find(
                (c) => c.iso2 === selectedCountryKey
            );
            if (selected) {
                setCountry(selected.name);
            }
        }
    }, [selectedCountryKey, fetchedCountries]);

    // Build dropdown options using the current language for display
    const dropdownOptions = fetchedCountries.map((c) => {
        // Use the translation for the current language, fallback to default name if not available
        const translatedName = c.translations[i18n.language] || c.name;
        return { key: c.iso2, value: translatedName };
    });

    // Handler for updating address
    const handleNameChangePress = async () => {
        if (!street.trim() || !zipCode.trim() || !city.trim() || !state.trim() || !country.trim()) {
            if (!street.trim()) setStreetError(true);
            if (!zipCode.trim()) setZipCodeError(true);
            if (!city.trim()) setCityError(true);
            if (!state.trim()) setStateError(true);
            if (!country.trim()) setCountryError(true);
            Toast.show({
                type: "error",
                text1: t("error_change_address_all_fields"),
                text2: t("error_fill_all_fields_address_subheading"),
            });
            return;
        }

        if (street === initialStreet && zipCode === initialZipCode && city === initialCity && state === initialState && country === initialCountry) {
            Toast.show({
                type: "error",
                text1: t("error_change_address_same"),
                text2: t("error_change_address_same_subheading"),
            });
            return;
        }

        try {
            // Call the changeAddress service using the default country name
            await changeAddress(street, zipCode, city, state, country);
            router.back();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("error_change_address_failed"),
                text2: t("error_change_address_failed_subheading"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
                    <View className="my-4">
                        <Heading text={t("change_address_heading")} />
                    </View>
                    <DefaultTextFieldInput
                        placeholder={t("change_street_placeholder")}
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
                        placeholder={t("change_zip_placeholder")}
                        value={zipCode}
                        onChangeText={(text) => {
                            setZipCode(text);
                            if (text.trim()) {
                                setZipCodeError(false);
                            }
                        }}
                        hasError={zipCodeError}
                    />
                    <DefaultTextFieldInput
                        placeholder={t("change_city_placeholder")}
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
                        placeholder={t("change_state_placeholder")}
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
                        placeholder={t("change_country_placeholder")}
                        save="key" 
                        defaultOption={
                            selectedCountryKey
                                ? {
                                    key: selectedCountryKey,
                                    value:
                                        fetchedCountries.find((c) => c.iso2 === selectedCountryKey)?.translations[i18n.language] ||
                                        initialCountry,
                                }
                                : undefined
                        }
                    />
                    <DefaultButton text={t("change_address_button")} onPress={handleNameChangePress} />
                    <DefaultToast />
                </View>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
};

export default SettingsChangeAddress;
