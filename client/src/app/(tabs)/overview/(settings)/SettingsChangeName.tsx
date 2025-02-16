import React from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";

const SettingsChangeName = () => {
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the name change settings page" />
        </View>
    );
};

export default SettingsChangeName;