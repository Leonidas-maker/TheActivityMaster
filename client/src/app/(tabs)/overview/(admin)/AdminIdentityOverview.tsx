import React, { useEffect, useState } from "react";
import { View, TouchableOpacity, Alert } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { getPendingVerification } from "@/src/services/verificiation/identityService";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

// Define the expected structure of a verification
interface Verification {
    id: string;
    user_id: string;
  }
  
  const AdminIdentityOverview: React.FC = () => {
    const { t } = useTranslation("admin");
    const router = useRouter();
    const [pendingVerifications, setPendingVerifications] = useState<Verification[]>([]);
  
    // Fetch pending verifications on component mount
    useEffect(() => {
      const fetchPendingVerifications = async () => {
        try {
          const data: Verification[] = await getPendingVerification();
          setPendingVerifications(data);
        } catch (error) {
          console.error("Failed to fetch pending verifications:", error);
        }
      };
  
      fetchPendingVerifications();
    }, []);
  
    // Handler for when a verification item is pressed
    const handlePress = (verificationId: string) => {
      router.navigate(`/(tabs)/overview/(admin)/AdminIdentityApprove?verification_id=${verificationId}`);
    };
  
    // Map the pending verifications to arrays expected by PageNavigator
    const texts = pendingVerifications.map(v => `Verification ID: ${v.id}`);
    const onPressFunctions = pendingVerifications.map(v => () => handlePress(v.id));
    // Using a default icon name for each verification item; adjust as needed
    const iconNames = pendingVerifications.map(() => "pending");
  
    return (
      <View className="h-screen  bg-light_primary dark:bg-dark_primary">
        <PageNavigator
          title="Pending Verifications"
          texts={texts}
          onPressFunctions={onPressFunctions}
          iconNames={iconNames}
        />
      </View>
    );
  };
  
  export default AdminIdentityOverview;