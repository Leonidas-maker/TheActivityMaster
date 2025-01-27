// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView } from "react-native";
import { expo } from "@/app.json";
import { Link, useRouter } from "expo-router";
import { clearAllStorage } from "@/src/services/clearStorage";
import { useTranslation } from "react-i18next";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import PageNavigator from '@/src/components/pageNavigator/PageNavigator';
import { goBack } from "expo-router/build/global-state/routing";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const OverviewHome: React.FC = () => {
  // ~~~~~~~~~~~ Define navigator ~~~~~~~~~~ //
  const router = useRouter();
  const { t } = useTranslation("overview");

  // ====================================================== //
  // =================== ModuleNavigator ================== //
  // ====================================================== //
  const handleSettingsPress = () => {
    router.navigate("/(tabs)/overview/(settings)/Settings");
  };

  const moduleTitle = t("pageNavigator_title1");

  const onPressModuleFunctions = [handleSettingsPress];

  const moduleTexts = [t("settings_btn")];

  const moduleIconNames = ["settings"];

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  // Returns the navigators and the current app version
  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <PageNavigator
        title={moduleTitle}
        onPressFunctions={onPressModuleFunctions}
        texts={moduleTexts}
        iconNames={moduleIconNames}
      />
      <View className="justify-center items-center my-2">
        <DefaultButton text={t("clear_storage_btn")} onPress={() => clearAllStorage()} />
      </View>
      <View className="justify-center items-center my-2">
        <DefaultText text={t("app_version") + `: ${expo.version} ❤️`} />
      </View>
    </ScrollView>
  );
};

export default OverviewHome;
