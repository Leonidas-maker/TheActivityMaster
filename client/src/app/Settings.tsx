import React, { useState, useEffect } from "react";
import { useColorScheme } from "nativewind";
import { useTheme  } from "@/src/provider/ThemeProvider";
import { View, ScrollView } from "react-native";
import Subheading from "@/src/components/textFields/Subheading";
import RadioOption from "@/src/components/radioOption/RadioOption";
import { useTranslation } from 'react-i18next';
import DefaultButton from "../components/buttons/DefaultButton";

const Settings: React.FC = () => {
  const [isLight, setIsLight] = useState(false);

  const { theme, setTheme } = useTheme();
  const { t, i18n } = useTranslation("settings");

  // ~~~~~~~~~~~~~~ Use Color Scheme ~~~~~~~~~~~~~~ //
  const { colorScheme, setColorScheme } = useColorScheme();

  // Set the color scheme
  useEffect(() => {
    setColorScheme(theme);
  }, [theme, setColorScheme]);

  // Set if the theme is light or dark
  useEffect(() => {
    if (colorScheme === "light") {
      setIsLight(true);
    } else {
      setIsLight(false);
    }
  }, [colorScheme]);

  // Color based on the theme
  const radioColor = isLight ? "#171717" : "#E0E2DB";

  const switchLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  //TODO: Make the language switcher a component with better styling
  return (
      <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
        <View className="p-4">
          <Subheading text={t("design_heading")} />
          <RadioOption
            label={t("light_mode")}
            onPress={() => setTheme("light")}
            checked={theme === "light"}
            radioColor={radioColor}
          />
          <RadioOption
            label={t("dark_mode")}
            onPress={() => setTheme("dark")}
            checked={theme === "dark"}
            radioColor={radioColor}
          />
          <RadioOption
            label={t("system_mode")}
            onPress={() => setTheme("system")}
            checked={theme === "system"}
            radioColor={radioColor}
          />
          <Subheading text={t("lang_heading")} />
          <DefaultButton text={t("en_btn")} onPress={() => switchLanguage("en")} />
          <DefaultButton text={t("de_btn")} onPress={() => switchLanguage("de")} />
        </View>
      </ScrollView>
  );
};

export default Settings;
