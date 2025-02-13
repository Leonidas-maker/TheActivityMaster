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
import Dropdown from "@/src/components/dropdown/Dropdown";
import StepProgressBar from "@/src/components/stepProgressBar/StepProgressBar";
import Subheading from "@/src/components/textFields/Subheading";

const SignUp: React.FC = () => {
    const { t } = useTranslation("auth");
    const router = useRouter();
    const { acceptedTerms: acceptedTermsParam } = useLocalSearchParams();

    // Step state and field states.
    const [currentStep, setCurrentStep] = useState(0);
    const totalSteps = 4;

    // Step 1: Email and Username.
    const [email, setEmail] = useState("");
    const [confirmEmail, setConfirmEmail] = useState("");
    const [username, setUsername] = useState("");

    // Step 2: Password, first and last name.
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");

    // Step 3: Personal Information.
    const [country, setCountry] = useState("Germany");
    const [street, setStreet] = useState("");
    const [city, setCity] = useState("");
    const [zip, setZip] = useState("");
    const [state, setState] = useState("");

    // Step 4: Additional Details.
    const [acceptedTerms, setAcceptedTerms] = useState(false);
    const [receiveNews, setReceiveNews] = useState(false);

    // Error states for the fields.
    const [emailError, setEmailError] = useState(false);
    const [confirmEmailError, setConfirmEmailError] = useState(false);
    const [passwordError, setPasswordError] = useState(false);
    const [confirmPasswordError, setConfirmPasswordError] = useState(false);
    const [usernameError, setUsernameError] = useState(false);
    const [firstNameError, setFirstNameError] = useState(false);
    const [lastNameError, setLastNameError] = useState(false);

    // Animated value for step content transitions.
    const fieldAnim = useRef(new Animated.Value(0)).current;
    const isInitialMount = useRef(true);

    // Helper function to check if an email is valid.
    const isValidEmail = (email: string): boolean => {
        const emailRegex = /^\S+@\S+\.\S+$/;
        return emailRegex.test(email);
    };

    useFocusEffect(
        useCallback(() => {
            if (acceptedTermsParam === "true") {
                setAcceptedTerms(true);
            }
        }, [acceptedTermsParam])
    );

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
                const totalFields = 3;
                const filled =
                    (email.trim() !== "" ? 1 : 0) +
                    (confirmEmail.trim() !== "" ? 1 : 0) +
                    (username.trim() !== "" ? 1 : 0);
                return filled / totalFields;
            }
            case 1: {
                const totalFields = 4;
                const filled =
                    (password.trim() !== "" ? 1 : 0) +
                    (confirmPassword.trim() !== "" ? 1 : 0) +
                    (firstName.trim() !== "" ? 1 : 0) +
                    (lastName.trim() !== "" ? 1 : 0);
                return filled / totalFields;
            }
            case 2: {
                const totalFields = 5;
                const filled =
                    (country.trim() !== "" ? 1 : 0) +
                    (street.trim() !== "" ? 1 : 0) +
                    (city.trim() !== "" ? 1 : 0) +
                    (zip.trim() !== "" ? 1 : 0) +
                    (state.trim() !== "" ? 1 : 0);
                return filled / totalFields;
            }
            case 3: {
                const totalFields = 1;
                const filled = acceptedTerms ? 1 : 0;
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
            // Check for empty fields.
            const isEmailEmpty = !email.trim();
            const isConfirmEmailEmpty = !confirmEmail.trim();
            const isUsernameEmpty = !username.trim();

            if (isEmailEmpty || isConfirmEmailEmpty || isUsernameEmpty) {
                if (isEmailEmpty) setEmailError(true);
                if (isConfirmEmailEmpty) setConfirmEmailError(true);
                if (isUsernameEmpty) setUsernameError(true);

                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
                return;
            }

            // Check if the provided emails are valid.
            if (!isValidEmail(email) || !isValidEmail(confirmEmail)) {
                setEmailError(true);
                setConfirmEmailError(true);
                Toast.show({
                    type: "error",
                    text1: t("emailInvalidError_text") || "Invalid Email Address",
                    text2: t("emailInvalidError_subtext") || "Please enter a valid email address.",
                });
                return;
            }

            // Check if emails match.
            if (email !== confirmEmail) {
                setEmailError(true);
                setConfirmEmailError(true);
                Toast.show({
                    type: "error",
                    text1: t("emailError_text"),
                    text2: t("emailError_subtext"),
                });
                return;
            } else {
                setEmailError(false);
                setConfirmEmailError(false);
            }
        }

        // Validate inputs for step 1 (Password and Personal Names).
        if (currentStep === 1) {
            const isFirstNameEmpty = !firstName.trim();
            const isLastNameEmpty = !lastName.trim();
            const isPasswordEmpty = !password.trim();
            const isConfirmPasswordEmpty = !confirmPassword.trim();

            if (isFirstNameEmpty || isLastNameEmpty || isPasswordEmpty || isConfirmPasswordEmpty) {
                if (isFirstNameEmpty) setFirstNameError(true);
                if (isLastNameEmpty) setLastNameError(true);
                if (isPasswordEmpty) setPasswordError(true);
                if (isConfirmPasswordEmpty) setConfirmPasswordError(true);

                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
                return;
            }

            // Check if the password is at least 8 characters long.
            if (password.length < 8) {
                setPasswordError(true);
                setConfirmPasswordError(true);
                Toast.show({
                    type: "error",
                    text1: t("passwordMinLengthError_text"),
                    text2: t("passwordMinLengthError_subtext"),
                });
                return;
            }

            // Check if passwords match.
            if (password !== confirmPassword) {
                setPasswordError(true);
                setConfirmPasswordError(true);
                Toast.show({
                    type: "error",
                    text1: t("passwordError_text"),
                    text2: t("passwordError_subtext"),
                });
                return;
            } else {
                setPasswordError(false);
                setConfirmPasswordError(false);
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
        if (!acceptedTerms) {
            Toast.show({
                type: "error",
                text1: t("termsError_text"),
                text2: t("termsError_subtext"),
            });
            return;
        }

        try {
            const response = await register(
                username,
                email,
                firstName,
                lastName,
                street,
                zip,
                city,
                state,
                country,
                password
            );

            router.replace("/auth/(info)/VerifyMail");
        } catch (error: any) {
            console.error("Registration error:", error);
            Toast.show({
                type: "error",
                text1: t("registrationError_text"),
                text2: t("registrationError_subtext"),
            });
        }
    };

    // The handleTerms function now just navigates to the Terms screen.
    const handleTerms = () => {
        if (!acceptedTerms) {
            router.push("/auth/(info)/Terms");
        } else {
            setAcceptedTerms(false);
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
                                    <Subheading text={t("registration_step1_title")} />
                                    <DefaultTextFieldInput
                                        placeholder={t("email_placeholder")}
                                        value={email}
                                        onChangeText={(text) => {
                                            setEmail(text);
                                            if (text.trim()) {
                                                setEmailError(false);
                                            }
                                        }}
                                        hasError={emailError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("confirm_email_placeholder")}
                                        value={confirmEmail}
                                        onChangeText={(text) => {
                                            setConfirmEmail(text);
                                            if (text.trim()) {
                                                setConfirmEmailError(false);
                                            }
                                        }}
                                        hasError={confirmEmailError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("username_placeholder")}
                                        value={username}
                                        onChangeText={(text) => {
                                            setUsername(text);
                                            if (text.trim()) {
                                                setUsernameError(false);
                                            }
                                        }}
                                        hasError={usernameError}
                                    />
                                </View>
                            )}
                            {currentStep === 1 && (
                                <View className="w-full items-center">
                                    <Subheading text={t("registration_step2_title")} />
                                    <DefaultTextFieldInput
                                        placeholder={t("password_placeholder")}
                                        secureTextEntry
                                        value={password}
                                        onChangeText={(text) => {
                                            setPassword(text);
                                            if (text.trim()) {
                                                setPasswordError(false);
                                            }
                                        }}
                                        hasError={passwordError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("confirm_password_placeholder")}
                                        secureTextEntry
                                        value={confirmPassword}
                                        onChangeText={(text) => {
                                            setConfirmPassword(text);
                                            if (text.trim()) {
                                                setConfirmPasswordError(false);
                                            }
                                        }}
                                        hasError={confirmPasswordError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("first_name_placeholder")}
                                        value={firstName}
                                        onChangeText={(text) => {
                                            setFirstName(text);
                                            if (text.trim()) {
                                                setFirstNameError(false);
                                            }
                                        }}
                                        hasError={firstNameError}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("last_name_placeholder")}
                                        value={lastName}
                                        onChangeText={(text) => {
                                            setLastName(text);
                                            if (text.trim()) {
                                                setLastNameError(false);
                                            }
                                        }}
                                        hasError={lastNameError}
                                    />
                                </View>
                            )}
                            {currentStep === 2 && (
                                <View className="w-full items-center">
                                    <Subheading text={t("registration_step3_title")} />
                                    <DefaultTextFieldInput
                                        placeholder={t("country_placeholder")}
                                        value={country}
                                        onChangeText={setCountry}
                                        editable={false}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("street_placeholder")}
                                        value={street}
                                        onChangeText={setStreet}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("city_placeholder")}
                                        value={city}
                                        onChangeText={setCity}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("zip_placeholder")}
                                        value={zip}
                                        onChangeText={setZip}
                                    />
                                    <DefaultTextFieldInput
                                        placeholder={t("state_placeholder")}
                                        value={state}
                                        onChangeText={setState}
                                    />
                                </View>
                            )}
                            {currentStep === 3 && (
                                <View className="w-full items-center">
                                    <Subheading text={t("registration_step4_title")} />
                                    <OptionSwitch
                                        title={t("more_information_title")}
                                        texts={[t("accept_terms_text"), t("receive_news_text")]}
                                        iconNames={["check", "mail"]}
                                        values={[acceptedTerms, receiveNews]}
                                        onValueChanges={[handleTerms, setReceiveNews]}
                                    />
                                </View>
                            )}
                        </Animated.View>

                        <View className="w-full items-center mt-6">
                            {currentStep < totalSteps - 1 ? (
                                <DefaultButton text={t("next_button")} onPress={handleNext} />
                            ) : (
                                <DefaultButton text={t("register_button")} onPress={handleSubmit} />
                            )}
                            {currentStep > 0 && <SecondaryButton text={t("back_button")} onPress={handleBack} />}
                        </View>

                        {currentStep === 0 && (
                            <View className="mt-4 w-full justify-center items-center">
                                <SecondaryButton text={t("already_have_account")} onPress={() => router.navigate("/auth")} />
                            </View>
                        )}
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default SignUp;