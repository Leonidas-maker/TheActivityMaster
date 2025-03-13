import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Alert, Pressable, TouchableWithoutFeedback, Keyboard, Platform, KeyboardAvoidingView } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import { deleteProgram, getProgram, updateProgram, getProgramCategories } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import Subheading from "@/src/components/textFields/Subheading";
import Dropdown from "@/src/components/dropdown/Dropdown";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
import { getSessions } from "@/src/services/club/programSessionService";
import { usePermissionContext } from "@/src/provider/PermissionProvider";

//TODO: Add change currency option
const UpdateProgram = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t, i18n } = useTranslation("clubs");
    const language = i18n.language;
    const { club_id, program_id } = useLocalSearchParams();
    const { hasPermission } = usePermissionContext();

    const [name, setName] = useState("");
    const [initialName, setInitialName] = useState("");
    const [description, setDescription] = useState("");
    const [initialDescription, setInitialDescription] = useState("");
    const [price, setPrice] = useState("");
    const [initialPrice, setInitialPrice] = useState("");
    const [currency, setCurrency] = useState("EUR");
    const [initialCurrency, setInitialCurrency] = useState("EUR");
    const [status, setStatus] = useState("");
    const [initialStatus, setInitialStatus] = useState("");
    const [capacity, setCapacity] = useState("");
    const [initialCapacity, setInitialCapacity] = useState("");
    const [pricingModel, setPricingModel] = useState("");
    const [initialPricingModel, setInitialPricingModel] = useState("");
    const [membershipRequired, setMembershipRequired] = useState(false);
    const [initialMembershipRequired, setInitialMembershipRequired] = useState(false);
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const [initialSelectedCategories, setInitialSelectedCategories] = useState<string[]>([]);
    const [nameError, setNameError] = useState(false);
    const [descriptionError, setDescriptionError] = useState(false);
    const [priceError, setPriceError] = useState(false);
    const [capacityError, setCapacityError] = useState(false);
    const [programCategories, setProgramCategories] = useState<Array<{ key: string; value: string }>>([]);

    useEffect(() => {
        const fetchProgramCategories = async () => {
            try {
                const categories = await getProgramCategories(language);
                setProgramCategories(
                    categories.map((category: any) => ({
                        key: category.id.toString(),
                        value: category.name
                    }))
                );
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchProgramCategories();
    }, [language]);

    useEffect(() => {
        const fetchProgram = async () => {
            try {
                const program = await getProgram(club_id, program_id);
                if (program) {
                    setName(program.name);
                    setInitialName(program.name);
                    setDescription(program.description);
                    setInitialDescription(program.description);
                    if (program.price && program.capacity) {
                        setPrice(program.price.toString());
                        setInitialPrice(program.price.toString());
                        setCapacity(program.capacity.toString());
                        setInitialCapacity(program.capacity.toString());
                    }
                    setPricingModel(program.pricing_model);
                    setInitialPricingModel(program.pricing_model);
                    setMembershipRequired(program.membership_required);
                    setInitialMembershipRequired(program.membership_required);
                    // Update the status if available from the API response.
                    if (program.status) {
                        setStatus(program.status);
                        setInitialStatus(program.status);
                    }
                    // Map over the categories array from the API response
                    setSelectedCategories(
                        program.categories.map((category: any) => category.id.toString())
                    );
                    setInitialSelectedCategories(program.categories.map((category: any) => category.id.toString()));
                }
            }
            catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            }
        };
        fetchProgram();
    }, [club_id, program_id]);

    // States for color scheme
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDeletePress = async () => {
        Alert.alert(t("programDeletionAlertTitle"), t("programDeletionAlertDescription"), [
            {
                text: t("cancel_btn"),
                style: "cancel"
            },
            {
                text: t("confirm_btn"),
                onPress: handleDeleteConfirm
            }
        ]);
    };

    const handleDeleteConfirm = async () => {
        try {
            await deleteProgram(club_id, program_id);
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };

    const handleDismissPress = () => {
        router.dismiss();
    };

    // Set navigation header buttons
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
            headerRight: () => (
                hasPermission("club_delete_programs") ? (
                    <Pressable onPress={handleDeletePress}>
                        <Icon
                            name="delete"
                            size={30}
                            color={iconColor}
                            style={{ marginLeft: "auto", marginRight: 15 }}
                        />
                    </Pressable>
                ) : null
            )
        });
    }, [navigation, iconColor]);

    const numericCategories = selectedCategories.map((key) => Number(key));
    const priceValue = pricingModel === "package" ? Number(price) : null;
    const capacityValue = pricingModel === "package" ? Number(capacity) : null;


    const handleUpdateProgramPress = async () => {
        // Use a local variable to track if there is any error
        let hasError = false;

        // Validate the name field
        if (!name.trim()) {
            setNameError(true);
            hasError = true;
        }

        // Validate the description field
        if (!description.trim()) {
            setDescriptionError(true);
            hasError = true;
        }

        if (description.length < 10) {
            setDescriptionError(true);
            Toast.show({
                type: "error",
                text1: t("descriptionError_text"),
                text2: t("descriptionError_subtext")
            });
            return;
        }

        // Only validate price and capacity if pricing model is "package"
        if (pricingModel === "package") {
            if (!price.trim()) {
                setPriceError(true);
                hasError = true;
            }
            if (!capacity.trim()) {
                setCapacityError(true);
                hasError = true;
            }
        } else if (pricingModel === "per_session") {
            setPriceError(false);
            setCapacityError(false);
        }

        // If any error is found, show an error toast and exit the function
        if (hasError) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext")
            });
            return;
        }

        if (name === initialName && description === initialDescription && price === initialPrice && currency === initialCurrency && pricingModel === initialPricingModel && capacity === initialCapacity && membershipRequired === initialMembershipRequired && numericCategories.length === initialSelectedCategories.length && numericCategories.every((value, index) => value === Number(initialSelectedCategories[index])) && status === initialStatus) {
            Toast.show({
                type: "info",
                text1: t("roleManageInfo"),
                text2: t("roleManageInfoDescription")
            });
            return;
        }

        let session_data = null;
        if (pricingModel === "package") {
            if (status === "active") {
                try {
                    const sessions = await getSessions(club_id, program_id);
                    if (sessions.length === 0) {
                        Toast.show({
                            type: "error",
                            text1: t("sessionError_text"),
                            text2: t("sessionError_subtext")
                        });
                        return;
                    }
                } catch (error) {
                    Toast.show({
                        type: "error",
                        text1: t("roleManageError"),
                        text2: t("roleManageErrorDescription")
                    });
                    return;
                }
            }
        } else if (pricingModel === "per_session") {
            try {
                const sessions = await getSessions(club_id, program_id);
                if (sessions.length === 0) {
                    Toast.show({
                        type: "error",
                        text1: t("sessionError_text"),
                        text2: t("sessionError_subtext")
                    });
                    return;
                }
                const sessionDataConstruct: { [key: string]: [number | null, number | null] } = {};
                sessions.forEach((session: any) => {
                    // If converting from package, update sessions with the package values; otherwise, retain the existing session values
                    if (initialPricingModel === "package") {
                        sessionDataConstruct[session.id] = [Number(price), Number(capacity)];
                    } else {
                        sessionDataConstruct[session.id] = [session.price, session.capacity];
                    }
                });
                session_data = sessionDataConstruct;
            } catch (error) {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
                return;
            }
        }

        try {
            const statusValue = status?.trim() && status === "draft" ? undefined : status;
            await updateProgram(
                club_id,
                program_id,
                name,
                description,
                pricingModel === "package" ? Number(price) : null,
                currency,
                pricingModel,
                pricingModel === "package" ? Number(capacity) : null,
                membershipRequired,
                selectedCategories.map((key) => Number(key)),
                session_data,
                statusValue
            );
            router.dismiss();
        } catch (error) {
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
        }
    };


    // Determine the available status options based on the current status.
    // "draft" option is only available if the current status is "draft".
    const statusOptions = status === "draft"
        ? [
            { key: "draft", value: t("draft") },
            { key: "active", value: t("active") },
            { key: "inactive", value: t("inactive") }
        ]
        : [
            { key: "active", value: t("active") },
            { key: "inactive", value: t("inactive") }
        ];

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("update_program_heading")} />
                        </View>
                        <Subheading text={t("program_detail_subheading")} />
                        <DefaultTextFieldInput
                            placeholder={t("program_name_placeholder")}
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
                            placeholder={t("program_description_placeholder")}
                            value={description}
                            onChangeText={(text) => {
                                setDescription(text);
                                if (text.trim()) {
                                    setDescriptionError(false);
                                }
                            }}
                            hasError={descriptionError}
                        />
                        <Subheading text={t("program_pricing_subheading")} />
                        <Dropdown
                            setSelected={(selected) => {
                                setPricingModel(selected);
                                setPriceError(false);
                                setCapacityError(false);
                            }}
                            values={[
                                { key: "package", value: t("package") },
                                { key: "per_session", value: t("per_session") }
                            ]}
                            placeholder={t("selectPricingModel_placeholder")}
                            defaultOption={{
                                key: pricingModel,
                                value: pricingModel === "package" ? t("package") : t("per_session")
                            }}
                            save="key"
                        />
                        <OptionSwitch
                            title={t("membership_required")}
                            texts={[t("enable_membership")]}
                            iconNames={["person"]}
                            values={[membershipRequired]}
                            onValueChanges={[
                                () => setMembershipRequired((prev) => !prev)
                            ]}
                        />
                        {pricingModel === "package" && (
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
                        <View className="w-full items-center justify-center pb-4">
                            <Subheading text={t("program_categories_placeholder")} />
                            <MultiDropdown
                                setSelected={setSelectedCategories}
                                initialSelected={selectedCategories}
                                values={programCategories}
                                placeholder={t("selectProgramCategories_placeholder")}
                                notFound={t("no_program_categories_found")}
                                searchPlaceholderText={t("search_program_categories_placeholder")}
                                useSections={false}
                                confirmButtonText={t("selectPermissions_confirmButton")}
                                maxSelectedItems={4}
                            />
                        </View>
                        <Subheading text={t("program_status_subheading")} />
                        <Dropdown
                            setSelected={setStatus}
                            values={statusOptions}
                            placeholder={t("selectStatus_placeholder")}
                            defaultOption={{
                                key: status,
                                value:
                                    status === "draft"
                                        ? t("draft")
                                        : status === "active"
                                            ? t("active")
                                            : t("inactive")
                            }}
                            save="key"
                        />
                        <View className="w-full items-center justify-center pb-4">
                            <DefaultButton text={t("program_update_btn")} onPress={handleUpdateProgramPress} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default UpdateProgram;
