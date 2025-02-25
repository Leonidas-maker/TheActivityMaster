import React, { useEffect, useState } from "react";
import { View, ScrollView, TouchableOpacity, Text } from "react-native";
// Import SafeAreaView to respect safe areas
import { SafeAreaView } from "react-native-safe-area-context";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getVerification } from "@/src/services/verificiation/identityService";
import VerificationImage from "@/src/components/images/VerificationImage";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { approveVerification, rejectVerification } from "@/src/services/verificiation/identityService";

//TODO: Add reasoning for rejecting verification
const AdminIdentityApprove = () => {
  const { t } = useTranslation("admin");
  const router = useRouter();
  const { verification_id } = useLocalSearchParams();

  // State for verification details and image URIs
  const [verificationId, setVerificationId] = useState<string>("");
  const [lastName, setLastName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [dob, setDob] = useState("");
  const [createdAt, setCreatedAt] = useState("");
  const [expiresAt, setExpiresAt] = useState("");

  useEffect(() => {
    const fetchVerification = async () => {
      try {
        // Get the verification ID from parameters (ensure it's a string)
        const id = Array.isArray(verification_id) ? verification_id[0] : verification_id;
        setVerificationId(id);

        // Fetch verification details
        const verification = await getVerification(id);
        setLastName(verification.last_name);
        setFirstName(verification.first_name);
        setDob(verification.date_of_birth);
        setCreatedAt(verification.created_at);
        setExpiresAt(verification.expires_at);
      } catch (error) {
        console.error("Failed to fetch verification:", error);
      }
    };

    fetchVerification();
  }, [verification_id]);

  const handleApprovePress = async () => {
    try {
      await approveVerification(verificationId);
      while (router.canGoBack()) {
        router.back();
      }
    } catch (error) {
      console.error("Failed to approve verification:", error);
    }
  }

  const handleRejectPress = async () => {
    try {
      await rejectVerification(verificationId, "Rejected by admin");
      while (router.canGoBack()) {
        router.back();
      }
    } catch (error) {
      console.error("Failed to reject verification:", error);
    }
  }

  return (
    <SafeAreaView edges={["left", "right"]} className="bg-light_primary dark:bg-dark_primary flex-1 px-2">
      <ScrollView>
        <View className="my-4">
          <Heading text={t("identityVerification_header")} />
        </View>

        <View className="justify-center items-center">
          <DefaultText text={t("first_name_text")} />
          <DefaultTextFieldInput editable={false} value={firstName} />
          <DefaultText text={t("last_name_text")} />
          <DefaultTextFieldInput editable={false} value={lastName} />
          <DefaultText text={t("dob_text")} />
          <DefaultTextFieldInput editable={false} value={dob} />
          <DefaultText text={t("created_at_text")} />
          <DefaultTextFieldInput editable={false} value={createdAt} />
          <DefaultText text={t("expires_at_text")} />
          <DefaultTextFieldInput editable={false} value={expiresAt} />
        </View>

        <View className="my-4">
          <VerificationImage verificationId={verificationId} index={0} />
        </View>
        <View className="my-4">
          <VerificationImage verificationId={verificationId} index={1} />
        </View>
        <View className="my-4">
          <VerificationImage verificationId={verificationId} index={2} />
        </View>
      </ScrollView>
      <View className="flex-row justify-around items-center border-t border-gray-200 dark:border-gray-700">
        {/* Decline button */}
        <TouchableOpacity
          onPress={handleRejectPress}
          className="p-6 rounded-md"
        >
          <Text style={{ color: "red", fontSize: 20, fontWeight: "bold" }}>
            {t("reject_btn")}
          </Text>
        </TouchableOpacity>
        {/* Accept button */}
        <TouchableOpacity
          onPress={handleApprovePress}
          className="p-6 rounded-md"
        >
          <Text style={{ color: "green", fontSize: 20, fontWeight: "bold" }}>
            {t("approve_btn")}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

export default AdminIdentityApprove;
