import React from "react";
import { View, ScrollView } from "react-native";
import Subheading from "@/src/components/textFields/Subheading";
import { useTranslation } from 'react-i18next';
import DefaultButton from "@/src/components/buttons/DefaultButton";
import OptionSelector from "@/src/components/optionSelector/OptionSelector";

const SettingsLanguage: React.FC = () => {
  const { t, i18n } = useTranslation("settings");

  const switchLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  const languageSelectorTitle = t("settings_lang_selector");

  const onPressLanguageFunctions = [() => switchLanguage("de"), () => switchLanguage("en")];

  const languageTexts = [t("de_btn"), t("en_btn")];

  const languageIconNames = ["🇩🇪", "🇺🇸"];

  const checkedLanguage = [i18n.language === "de", i18n.language === "en"];
  
  return (
      <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
        <OptionSelector 
          title={languageSelectorTitle}
          onPressFunctions={onPressLanguageFunctions}
          texts={languageTexts}
          iconNames={languageIconNames}
          checked={checkedLanguage}
          isEmoji={true}
        />
      </ScrollView>
  );
};

export default SettingsLanguage;
