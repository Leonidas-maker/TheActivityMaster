import DefaultText from "@/src/components/textFields/DefaultText";
import React from "react";
import { View } from "react-native";

const SettingsLogout = () => {
    //TODO: Implement logout functionality when API is ready
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the logout settings page" />
        </View>
    );
};

export default SettingsLogout;