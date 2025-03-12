import React, { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  useColorScheme,
  Pressable,
  TouchableWithoutFeedback,
  Keyboard,
  KeyboardAvoidingView,
  Platform
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { createMembership } from "@/src/services/club/membershipService";
import Dropdown from "@/src/components/dropdown/Dropdown";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Subheading from "@/src/components/textFields/Subheading";

const AddMembership = () => {
  const router = useRouter();
  const navigation = useNavigation();
  const { t, i18n } = useTranslation("clubs");
  const { club_id } = useLocalSearchParams();
  const language = i18n.language;
  const colorScheme = useColorScheme();
  const isLight = colorScheme === "light";
  const iconColor = isLight ? "#000000" : "#FFFFFF";

  // Form fields state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState("");
  const [durationUnit, setDurationUnit] = useState("month");
  const [currency, setCurrency] = useState("EUR");
  const [status, setStatus] = useState("draft");

  // Error states
  const [nameError, setNameError] = useState(false);
  const [descriptionError, setDescriptionError] = useState(false);
  const [priceError, setPriceError] = useState(false);
  const [durationError, setDurationError] = useState(false);

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

  const handleCreateMembershipPress = async () => {
    // Reset errors
    setNameError(false);
    setDescriptionError(false);
    setPriceError(false);
    setDurationError(false);

    if (!name.trim()) {
      setNameError(true);
    }
    if (!description.trim()) {
      setDescriptionError(true);
    }
    if (!price.trim() || isNaN(Number(price))) {
      setPriceError(true);
    }
    if (!duration.trim() || isNaN(Number(duration))) {
      setDurationError(true);
    }

    if (nameError || descriptionError || priceError || durationError) {
      Toast.show({
        type: "error",
        text1: t("inputError_text"),
        text2: t("inputError_subtext"),
      });
      return;
    }

    if (description.trim().length < 10) {
      setDescriptionError(true);
      Toast.show({
        type: "error",
        text1: t("descriptionError_text"),
        text2: t("descriptionError_subtext"),
      });
      return;
    }

    const priceValue = Number(price);
    const durationValue = Number(duration);

    try {
      await createMembership(
        club_id,
        name,
        description,
        priceValue,
        currency,
        durationValue,
        durationUnit,
        status
      );
      router.dismiss();
    } catch (error) {
      console.error("Error creating membership:", error);
      Toast.show({
        type: "error",
        text1: t("roleManageError"),
        text2: t("roleManageErrorDescription"),
      });
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1"
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
          <View className="items-center">
            <View className="py-4">
              <Heading text={t("create_membership_heading")} />
            </View>
            <DefaultTextFieldInput
              placeholder={t("membership_name_placeholder")}
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
              placeholder={t("membership_description_placeholder")}
              value={description}
              onChangeText={(text) => {
                setDescription(text);
                if (text.trim()) {
                  setDescriptionError(false);
                }
              }}
              hasError={descriptionError}
            />
            <DefaultTextFieldInput
              placeholder={t("program_price_placeholder")}
              value={price}
              onChangeText={(text) => {
                setPrice(text);
                if (text.trim() && !isNaN(Number(text))) {
                  setPriceError(false);
                }
              }}
              hasError={priceError}
            />
            <Subheading text={t("membership_duration_subheading")} />
            <DefaultTextFieldInput
              placeholder={t("membership_duration_placeholder")}
              value={duration}
              onChangeText={(text) => {
                setDuration(text);
                if (text.trim() && !isNaN(Number(text))) {
                  setDurationError(false);
                }
              }}
              hasError={durationError}
            />
            <Dropdown
              setSelected={(selected) => {
                setDurationUnit(selected);
              }}
              values={[
                { key: "day", value: t("day") },
                { key: "month", value: t("month") },
              ]}
              placeholder={t("selectDurationUnit_placeholder")}
              save="key"
            />
            <Subheading text={t("membership_status_subheading")} />
            <Dropdown
              setSelected={(selected) => {
                setStatus(selected);
              }}
              values={[
                { key: "draft", value: t("draft") },
                { key: "bookable", value: t("bookable") },
                { key: "not_bookable", value: t("not_bookable") }
              ]}
              placeholder={t("selectStatus_placeholder")}
              save="key"
            />
            <View className="w-full items-center justify-center pb-4">
              {/* Additional membership fields can be added here if needed */}
            </View>
            <DefaultButton
              text={t("membership_create_btn")}
              onPress={handleCreateMembershipPress}
            />
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
      <DefaultToast />
    </KeyboardAvoidingView>
  );
};

export default AddMembership;