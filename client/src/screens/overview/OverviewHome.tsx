// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView } from "react-native";
import { expo } from "../../../app.json";
import { useNavigation } from "@react-navigation/native";
import { clearAllStorage } from "../../services/clearStorage";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import PageNavigator from "../../components/pageNavigator/PageNavigator";
import DefaultText from "../../components/textFields/DefaultText";
import DefaultButton from "../../components/buttons/DefaultButton";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const OverviewHome: React.FC = () => {
  // ~~~~~~~~~~~ Define navigator ~~~~~~~~~~ //
  const navigation = useNavigation<any>();

  // ====================================================== //
  // =================== ModuleNavigator ================== //
  // ====================================================== //
  const handleSettingsPress = () => {
    navigation.navigate("Settings");
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
