// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView } from "react-native";
import { expo } from "@/app.json";
import { useRouter } from "expo-router";
import { clearAllStorage } from "@/src/services/clearStorage";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultText from "@/src/components/textFields/DefaultText";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import PageNavigator from '@/src/components/pageNavigator/PageNavigator';

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const OverviewHome: React.FC = () => {
  // ~~~~~~~~~~~ Define navigator ~~~~~~~~~~ //
  const router = useRouter(); // Den Router definieren

  // ====================================================== //
  // =================== ModuleNavigator ================== //
  // ====================================================== //
  const handleSettingsPress = () => {
    router.navigate("../settings/Settings");
    params: { previousRoute: '/(tabs)/OverviewHome' }
  };

  const moduleTitle = "Einstellungen";

  const onPressModuleFunctions = [handleSettingsPress];

  const moduleTexts = ["Einstellungen"];

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
        <DefaultButton text="Clear Storage" onPress={() => clearAllStorage()} />
      </View>
      <View className="justify-center items-center my-2">
        <DefaultText text={`App Version: ${expo.version} ❤️`} />
      </View>
    </ScrollView>
  );
};

export default OverviewHome;
