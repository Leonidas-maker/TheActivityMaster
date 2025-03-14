// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView, Linking } from "react-native";
import { useTranslation } from 'react-i18next';

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const BugReport = () => {
  const { t } = useTranslation("overview");

  // ====================================================== //
  // =================== Press handlers =================== //
  // ====================================================== //
  const handleGitLabPress = () => {
    Linking.openURL("https://gitlab.com/themastercollection/theactivitymaster");
  };

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <View className="px-5 py-5">
        <View className="mb-5">
          <Heading text={t('bugreport_heading')} />
        </View>
        <View className="flex-1 m-5">
          <View className="mb-3">
            <DefaultText text={t('bugreport_body1')} />
          </View>
          <DefaultText text={t('bugreport_body2')} />
        </View>
        <View className="content-center items-center">
          <DefaultButton
            text={t('bugreport_button')}
            onPress={handleGitLabPress}
          />
        </View>
      </View>
    </ScrollView>
  );
};

export default BugReport;
