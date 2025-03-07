import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Pressable, TouchableWithoutFeedback, Keyboard, KeyboardAvoidingView, Platform } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { createProgram, getProgramCategories } from "@/src/services/club/programService";
import Dropdown from "@/src/components/dropdown/Dropdown";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import OptionSwitch from "@/src/components/optionSwitch/OptionSwitch";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Subheading from "@/src/components/textFields/Subheading";

const AddProgram = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t, i18n } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();
    const language = i18n.language;

    // Form fields state
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [nameError, setNameError] = useState(false);
    const [descriptionError, setDescriptionError] = useState(false);
    const [price, setPrice] = useState("");
    const [priceError, setPriceError] = useState(false);
    const [pricingModel, setPricingModel] = useState("");
    const [pricingModelError, setPricingModelError] = useState(false);
    const [capacity, setCapacity] = useState("");
    const [capacityError, setCapacityError] = useState(false);
    const [membershipRequired, setMembershipRequired] = useState(false);
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const [programCategories, setProgramCategories] = useState<{ key: string; value: string }[]>([]);
    const [currency, setCurrency] = useState("EUR");
    const [status, setStatus] = useState<"active" | "inactive" | "draft">("draft");
    const [priceValue, setPriceValue] = useState<number | null>(null);
    const [capacityValue, setCapacityValue] = useState<number | null>(null);

    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

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
    }, [navigation, iconColor]);

    // Fetch available program categories on mount
    useEffect(() => {
        getProgramCategories(language)
            .then((response) => {
                const categoriesOptions = response.map((category: { id: number; name: string; description: string }) => ({
                    key: category.id.toString(),
                    value: category.name,
                }));
                setProgramCategories(categoriesOptions);
            })
            .catch((err) => {
                console.error("Error fetching program categories:", err);
            });
    }, []);

    const handleCreateProgramPress = async () => {
        if (!name.trim()) {
            setNameError(true);
        }
        if (!description.trim()) {
            setDescriptionError(true);
        }

        if (nameError || descriptionError) {
            Toast.show({
                type: "error",
                text1: t("inputError_text"),
                text2: t("inputError_subtext"),
            });
            return;
        }

        if (description.length < 10) {
            setDescriptionError(true);
            Toast.show({
                type: "error",
                text1: t("descriptionError_text"),
                text2: t("descriptionError_subtext"),
            });
            return;
        }

        if (!pricingModel.trim()) {
            Toast.show({
                type: "error",
                text1: t("pricingModelError_text"),
                text2: t("pricingModelError_subtext"),
            });
            return;
        }

        // Check pricingModel specific validations
        if (pricingModel === t("package")) {
            let packageError = false;
            if (!price.trim()) {
                setPriceError(true);
                packageError = true;
            }
            if (!capacity.trim()) {
                setCapacityError(true);
                packageError = true;
            }
            if (packageError) {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
                return;
            }
        }

        // Convert string keys to numbers.
        const numericCategories = selectedCategories.map((key) => Number(key));
        const priceValue = pricingModel === "package" ? Number(price) : null;
        const capacityValue = pricingModel === "package" ? Number(capacity) : null;

        try {
            await createProgram(
                club_id,
                name,
                description,
                priceValue,
                currency,
                pricingModel,
                capacityValue,
                membershipRequired,
                numericCategories,
                status
            );
            router.dismiss();
        } catch (error) {
            console.error("Error creating program:", error);
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription"),
            });
        }
    };

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("create_program_heading")} />
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
                                values={programCategories}
                                placeholder={t("selectProgramCategories_placeholder")}
                                notFound={t("no_program_categories_found")}
                                searchPlaceholderText={t("search_program_categories_placeholder")}
                                useSections={false}
                                confirmButtonText={t("selectPermissions_confirmButton")}
                                maxSelectedItems={4}
                            />
                        </View>
                        <DefaultButton text={t("program_create_btn")} onPress={handleCreateProgramPress} />
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default AddProgram;
