import React, { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  Pressable,
  useColorScheme,
  Keyboard,
  TouchableWithoutFeedback,
  KeyboardAvoidingView,
  Platform,
  Alert
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import { updateMembershipAccess, deleteMembershipAccess } from "@/src/services/club/membershipService";

const ManageProgramMembershipAccess = () => {
  const router = useRouter();
  const navigation = useNavigation();
  const { t } = useTranslation("clubs");
  const { club_id, membership_id, program_access } = useLocalSearchParams();

  // Color scheme state
  const [isLight, setIsLight] = useState(false);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setIsLight(colorScheme === "light");
  }, [colorScheme]);
  const iconColor = isLight ? "#000000" : "#FFFFFF";

  // State for additional fee and program ID
  const [fee, setFee] = useState("");
  const [initialFee, setInitialFee] = useState("");
  const [programId, setProgramId] = useState("");

  // Decode program_access query param and set fee and programId
  useEffect(() => {
    if (program_access) {
      try {
        const decoded = JSON.parse(decodeURIComponent(program_access as string));
        setFee(decoded.additional_fee !== undefined ? decoded.additional_fee.toString() : "");
        setInitialFee(decoded.additional_fee !== undefined ? decoded.additional_fee.toString() : "");
        setProgramId(decoded.program_id);
      } catch (error) {
        console.error("Failed to decode program_access:", error);
      }
    }
  }, [program_access]);

  // Function to dismiss the screen
  const handleDismissPress = () => {
    router.dismiss();
  };

  // Update header with a close button on the left and a delete button on the right
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
        <Pressable onPress={handleDeletePress}>
          <Icon
            name="delete"
            size={30}
            color={iconColor}
            style={{ marginRight: 15 }}
          />
        </Pressable>
      )
    });
  }, [navigation, iconColor]);

  // Handle update fees button press
  const handleUpdateFeesPress = async () => {
    // Check if fee has been modified
    if (fee === initialFee) {
      Toast.show({
        type: "info",
        text1: t("roleManageInfo"),
        text2: t("roleManageInfoDescription")
      });
      return;
    }
    try {
      await updateMembershipAccess(club_id, membership_id, programId, Number(fee));
      router.dismiss();
    } catch (error) {
      Toast.show({
        type: "error",
        text1: t("roleManageError"),
        text2: t("roleManageErrorDescription")
      });
    }
  };

  // Handle deletion of membership access
  const handleDeleteAccess = async () => {
    try {
      await deleteMembershipAccess(club_id, membership_id, programId);
      router.dismiss();
    } catch (error) {
      Toast.show({
        type: "error",
        text1: t("roleManageError"),
        text2: t("roleManageErrorDescription")
      });
    }
  };

  // Show confirmation alert before deletion
  const handleDeletePress = () => {
    Alert.alert(
      t("delete_access"),
      t("confirm_delete_access"),
      [
        { text: t("cancel_btn"), style: "cancel" },
        { text: t("confirm_btn"), style: "destructive", onPress: handleDeleteAccess }
      ]
    );
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
          <View className="items-center">
            <View className="py-4">
              {/* Heading can be adjusted to a relevant translation key if needed */}
              <Heading text={t("manage_program_access_heading")} />
            </View>
            <DefaultTextFieldInput
              placeholder={t("additionalFee_placeholder")}
              value={fee}
              onChangeText={(text) => setFee(text)}
            />
            <View className="w-full items-center justify-center pb-4">
              <DefaultButton text={t("update_fees_btn")} onPress={handleUpdateFeesPress} />
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
      <DefaultToast />
    </KeyboardAvoidingView>
  );
};

export default ManageProgramMembershipAccess;