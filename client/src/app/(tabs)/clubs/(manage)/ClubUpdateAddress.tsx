import React, { useState, useEffect } from "react";
import { ScrollView, View, Keyboard, KeyboardAvoidingView, Platform, TouchableWithoutFeedback } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getClub, updateClubAddress } from "@/src/services/club/clubService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Dropdown from "@/src/components/dropdown/Dropdown";
import { getCountries } from "@/src/services/static/countryService";

interface address {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
}

const ClubUpdateAddress = () => {
    const router = useRouter();
    const { t, i18n } = useTranslation("clubs");

    const { club_id } = useLocalSearchParams();

    const [street, setStreet] = useState("");
    const [zip, setZip] = useState("");
    const [city, setCity] = useState("");
    const [state, setState] = useState("");
    const [country, setCountry] = useState("");
    const [initialStreet, setInitialStreet] = useState("");
    const [initialZip, setInitialZip] = useState("");
    const [initialCity, setInitialCity] = useState("");
    const [initialState, setInitialState] = useState("");
    const [initialCountry, setInitialCountry] = useState("");
    const [address, setAddress] = useState<address>({
        street: "",
        postal_code: "",
        city: "",
        state: "",
        country: ""
    })
    const [streetError, setStreetError] = useState(false);
    const [zipError, setZipError] = useState(false);
    const [cityError, setCityError] = useState(false);
    const [stateError, setStateError] = useState(false);
    const [countryError, setCountryError] = useState(false);

    // State to hold full list of countries fetched from the API
    const [fetchedCountries, setFetchedCountries] = useState<any[]>([]);
    // Track the selected country's ISO2 code from the dropdown
    const [selectedCountryKey, setSelectedCountryKey] = useState("");

    useEffect(() => {
        const fetchClub = async () => {
            try {
                const club = await getClub(club_id);
                setStreet(club.address.street);
                setZip(club.address.postal_code);
                setCity(club.address.city);
                setState(club.address.state);
                setCountry(club.address.country);
                setInitialStreet(club.address.street);
                setInitialZip(club.address.postal_code);
                setInitialCity(club.address.city);
                setInitialState(club.address.state);
                setInitialCountry(club.address.country);
            } catch (error) {
                console.error("Error during fetchClub call:", error);
            }
        };
        fetchClub();
    }, []);

    const onUpdatePress = async () => {
        const isCountryEmpty = !country.trim();
        const isStateEmpty = !state.trim();
        const isStreetEmpty = !street.trim();
        const isZipEmpty = !zip.trim();
        const isCityEmpty = !city.trim();

        if (isCountryEmpty || isStateEmpty || isStreetEmpty || isZipEmpty || isCityEmpty) {
            if (isCountryEmpty) setCountryError(true);
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

        if (street === initialStreet && zip === initialZip && city === initialCity && state === initialState && country === initialCountry) {
            Toast.show({
                type: "error",
                text1: t("updateError_text"),
                text2: t("updateError_subtext")
            });
            return;
        }

        const newAddress = {
            street,
            postal_code: zip,
            city,
            state,
            country
        };

        try {
            await updateClubAddress(club_id, newAddress);
            router.back();
        } catch (error) {
            console.error("Error during updateClubAddress call:", error);
            Toast.show({
                type: "error",
                text1: t("updateErrorCall_text"),
                text2: t("updateErrorCall_subtext")
            });
        }
    };

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

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="w-full items-center">
                        <View className="py-4">
                            <Heading text={t("creation_step2_title")} />
                        </View>
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
                        <DefaultButton text={t("address_update_button")} onPress={onUpdatePress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
}

export default ClubUpdateAddress;