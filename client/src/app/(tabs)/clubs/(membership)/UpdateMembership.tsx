import React, { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  Pressable,
  useColorScheme,
  Keyboard,
  TouchableWithoutFeedback,
  KeyboardAvoidingView,
  Platform
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import Dropdown from "@/src/components/dropdown/Dropdown";
import { getMembership, updateMembership } from "@/src/services/club/membershipService";
import Subheading from "@/src/components/textFields/Subheading";

const UpdateMembership = () => {
  const router = useRouter();
  const navigation = useNavigation();
  const { t } = useTranslation("clubs");
  const { club_id, membership_id } = useLocalSearchParams();

  // Color scheme state
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
      )
    });
  }, [navigation, iconColor]);

  // State for membership details
  const [name, setName] = useState("");
  const [initialName, setInitialName] = useState("");
  const [description, setDescription] = useState("");
  const [initialDescription, setInitialDescription] = useState("");
  const [price, setPrice] = useState("");
  const [initialPrice, setInitialPrice] = useState("");
  const [currency, setCurrency] = useState("EUR");
  const [initialCurrency, setInitialCurrency] = useState("EUR");
  const [duration, setDuration] = useState("");
  const [initialDuration, setInitialDuration] = useState("");
  const [durationUnit, setDurationUnit] = useState("month");
  const [initialDurationUnit, setInitialDurationUnit] = useState("month");
  const [status, setStatus] = useState("");
  const [initialStatus, setInitialStatus] = useState("");

  // Error states
  const [nameError, setNameError] = useState(false);
  const [descriptionError, setDescriptionError] = useState(false);
  const [priceError, setPriceError] = useState(false);
  const [durationError, setDurationError] = useState(false);

  // Load current membership information
  useEffect(() => {
    const fetchMembership = async () => {
      try {
        const membership = await getMembership(club_id, membership_id);
        if (membership) {
          setName(membership.name);
          setInitialName(membership.name);
          setDescription(membership.description);
          setInitialDescription(membership.description);
          setPrice(membership.price?.toString() || "");
          setInitialPrice(membership.price?.toString() || "");
          setCurrency(membership.currency || "EUR");
          setInitialCurrency(membership.currency || "EUR");
          setDuration(membership.duration?.toString() || "");
          setInitialDuration(membership.duration?.toString() || "");
          setDurationUnit(membership.duration_unit || "month");
          setInitialDurationUnit(membership.duration_unit || "month");
          setStatus(membership.status);
          setInitialStatus(membership.status);
        }
      } catch (error) {
        Toast.show({
          type: "error",
          text1: t("roleManageError"),
          text2: t("roleManageErrorDescription")
        });
      }
    };
    fetchMembership();
  }, [club_id, membership_id, t]);

  // Determine status options.
  // If the membership is still draft, allow "draft", "bookable", and "not_bookable".
  // Once updated out of draft, do not allow switching back to draft.
  const statusOptions = initialStatus === "draft"
    ? [
        { key: "draft", value: t("draft") },
        { key: "bookable", value: t("bookable") },
        { key: "not_bookable", value: t("not_bookable") }
      ]
    : [
        { key: "bookable", value: t("bookable") },
        { key: "not_bookable", value: t("not_bookable") }
      ];

  const handleUpdateMembershipPress = async () => {
    // Reset error states
    setNameError(false);
    setDescriptionError(false);
    setPriceError(false);
    setDurationError(false);

    let hasError = false;
    if (!name.trim()) {
      setNameError(true);
      hasError = true;
    }
    if (!description.trim()) {
      setDescriptionError(true);
      hasError = true;
    }
    if (description.trim().length < 10) {
      setDescriptionError(true);
      Toast.show({
        type: "error",
        text1: t("descriptionError_text"),
        text2: t("descriptionError_subtext")
      });
      return;
    }
    if (!price.trim() || isNaN(Number(price))) {
      setPriceError(true);
      hasError = true;
    }
    if (!duration.trim() || isNaN(Number(duration))) {
      setDurationError(true);
      hasError = true;
    }
    if (hasError) {
      Toast.show({
        type: "error",
        text1: t("inputError_text"),
        text2: t("inputError_subtext")
      });
      return;
    }

    // Check if no field has been modified
    if (
      name === initialName &&
      description === initialDescription &&
      price === initialPrice &&
      duration === initialDuration &&
      durationUnit === initialDurationUnit &&
      status === initialStatus
    ) {
      Toast.show({
        type: "info",
        text1: t("roleManageInfo"),
        text2: t("roleManageInfoDescription")
      });
      return;
    }

    try {
      await updateMembership(
        club_id,
        membership_id,
        name,
        description,
        Number(price),
        currency,
        Number(duration),
        durationUnit,
        status
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

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
          <View className="items-center">
            <View className="py-4">
              <Heading text={t("update_membership_heading")} />
            </View>
            <DefaultTextFieldInput
              placeholder={t("membership_name_placeholder")}
              value={name}
              onChangeText={(text) => {
                setName(text);
                if (text.trim()) setNameError(false);
              }}
              hasError={nameError}
            />
            <DefaultTextFieldInput
              placeholder={t("membership_description_placeholder")}
              value={description}
              onChangeText={(text) => {
                setDescription(text);
                if (text.trim()) setDescriptionError(false);
              }}
              hasError={descriptionError}
            />
            <DefaultTextFieldInput
              placeholder={t("program_price_placeholder")}
              value={price}
              onChangeText={(text) => {
                setPrice(text);
                if (text.trim() && !isNaN(Number(text))) setPriceError(false);
              }}
              hasError={priceError}
            />
            <Subheading text={t("membership_duration_subheading")} />
            <DefaultTextFieldInput
              placeholder={t("membership_duration_placeholder")}
              value={duration}
              onChangeText={(text) => {
                setDuration(text);
                if (text.trim() && !isNaN(Number(text))) setDurationError(false);
              }}
              hasError={durationError}
            />
            <Dropdown
              setSelected={(selected) => setDurationUnit(selected)}
              values={[
                { key: "day", value: t("day") },
                { key: "month", value: t("month") },
              ]}
              placeholder={t("selectDurationUnit_placeholder")}
              defaultOption={{ key: durationUnit, value: t(durationUnit) }}
              save="key"
            />
            <Subheading text={t("membership_status_subheading")} />
            <Dropdown
              setSelected={setStatus}
              values={statusOptions}
              placeholder={t("selectStatus_placeholder")}
              defaultOption={{
                key: status,
                value:
                  status === "draft"
                    ? t("draft")
                    : status === "bookable"
                      ? t("bookable")
                      : t("not_bookable")
              }}
              save="key"
            />
            <View className="w-full items-center justify-center pb-4">
              <DefaultButton text={t("membership_update_btn")} onPress={handleUpdateMembershipPress} />
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
      <DefaultToast />
    </KeyboardAvoidingView>
  );
};

export default UpdateMembership;