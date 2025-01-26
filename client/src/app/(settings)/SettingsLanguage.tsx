import React from "react";
import { View, ScrollView } from "react-native";
import Subheading from "@/src/components/textFields/Subheading";
import { useTranslation } from 'react-i18next';
import DefaultButton from "@/src/components/buttons/DefaultButton";

const SettingsLanguage: React.FC = () => {
  const { t, i18n } = useTranslation("settings");

  const switchLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  //TODO: Make the language switcher a component with better styling
  return (
      <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
        <View className="p-4">
          <Subheading text={t("lang_heading")} />
          <DefaultButton text={t("en_btn")} onPress={() => switchLanguage("en")} />
          <DefaultButton text={t("de_btn")} onPress={() => switchLanguage("de")} />
        </View>
      </ScrollView>
  );
};

export default SettingsLanguage;
