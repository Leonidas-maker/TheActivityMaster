import React, { useEffect } from "react";
import { View } from "react-native";
import * as Linking from 'expo-linking'; // Import Expo Linking module
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";

export default function Tab() {
  const { t } = useTranslation("discover");

  useEffect(() => {
    // Handler for processing incoming deep links
    const handleDeepLink = (event: any) => {
      const url = event.url;
      console.log("Received deep link: ", url);
      // You can parse the URL here and navigate accordingly.
    };

    // Subscribe to the Linking event
    const subscription = Linking.addEventListener('url', handleDeepLink);

    // Check if the app was launched with a deep link
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink({ url });
      }
    });

    // Clean up the event listener on unmount
    return () => {
      subscription.remove();
    };
  }, []);

  return (
    <View className="flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary">
      <DefaultText text={t("test_text")} />
    </View>
  );
}
