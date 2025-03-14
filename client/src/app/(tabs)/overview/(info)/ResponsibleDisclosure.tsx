// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView, Linking } from "react-native";
import { useTranslation } from 'react-i18next';

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import TextButton from "@/src/components/buttons/TextButton";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const ResponsibleDisclosure = () => {
  const { t } = useTranslation("overview");
  
  // ====================================================== //
  // =================== Press handlers =================== //
  // ====================================================== //
  const handleMailPress = () => {
    Linking.openURL("mailto:responsible_disclosure@theactivitymaster.de");
  };

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <View className="px-5 py-5">
        <View className="mb-5">
          <Heading text={t('responsible_disclosure_heading')} />
        </View>
        <View className="flex-1 m-5">
          <View className="mb-3">
            <DefaultText text={t('responsible_disclosure_body')} />
          </View>
          <TextButton
            text="responsible_disclosure@theactivitymaster.de"
            onPress={handleMailPress}
          />
        </View>
      </View>
    </ScrollView>
  );
};

export default ResponsibleDisclosure;
