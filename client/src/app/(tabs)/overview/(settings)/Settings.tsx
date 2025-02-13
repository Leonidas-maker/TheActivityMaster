import React from "react";
import { ScrollView } from "react-native";
import { useTranslation } from 'react-i18next';
import { useRouter } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const Settings: React.FC = () => {
  const { t } = useTranslation("settings");

  const router = useRouter();

  // ====================================================== //
  // ================== SettingsNavigator ================= //
  // ====================================================== //
  const handleThemePress = () => {
    router.navigate("/(tabs)/overview/(settings)/SettingsTheme");
  };

  const handleLanguagePress = () => {
    router.navigate("/(tabs)/overview/(settings)/SettingsLanguage");
  };

  const moduleTitle = t("settingsPageNavigator_title1");

  const onPressModuleFunctions = [handleThemePress, handleLanguagePress];

  const moduleTexts = [t("settings_theme_btn"), t("settings_lang_btn")];

  const moduleIconNames = ["contrast", "language"];

  // ====================================================== //
  // ==================== UserNavigator ==================== //
  // ====================================================== //

  const handleUserPress = () => {
    router.navigate("/(tabs)/overview/(settings)/SettingsUser");
  };

  const handleSecurityPress = () => {
    router.navigate("/(tabs)/overview/(settings)/SettingsSecurity");
  };

  const handleNotificationsPress = () => {
    router.navigate("/(tabs)/overview/(settings)/SettingsNotifications");
  };

  const onPressUserFunctions = [handleUserPress, handleSecurityPress, handleNotificationsPress];

  const userTexts = [t("settings_user_btn"), t("settings_security_btn"), t("settings_notifications_btn")];

  const userIconNames = ["person", "shield", "notifications"];

  const userModuleTitle = t("accountSettingsPageNavigator_title");

  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <PageNavigator
        title={moduleTitle}
        onPressFunctions={onPressModuleFunctions}
        texts={moduleTexts}
        iconNames={moduleIconNames}
      />
      <PageNavigator
        title={userModuleTitle}
        onPressFunctions={onPressUserFunctions}
        texts={userTexts}
        iconNames={userIconNames}
      />
    </ScrollView>
  );
};

export default Settings;
