// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView, Linking } from "react-native";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import TextButton from "@/src/components/buttons/TextButton";
import Heading from "@/src/components/textFields/Heading";
import DefaultText from "@/src/components/textFields/DefaultText";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const Support = () => {
  // ====================================================== //
  // =================== Press handlers =================== //
  // ====================================================== //
  const handleMailPress = () => {
    Linking.openURL("mailto:support@theactivitymaster.de");
  };

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
      <View className="px-5 py-5">
        <View className="mb-5">
          <Heading text="Du benötigst Hilfe oder hast eine Frage?" />
        </View>
        <View className="flex-1 m-5">
          <View className="mb-3">
            <DefaultText text="Schreib uns bitte eine E-Mail an die unten stehende Adresse und wir werden versuchen dir so schnell wie möglich weiterzuhelfen." />
          </View>
          <TextButton
            text="support@theactivitymaster.de"
            onPress={handleMailPress}
          />
        </View>
      </View>
    </ScrollView>
  );
};

export default Support;
