import DefaultText from "@/src/components/textFields/DefaultText";
import React from "react";
import { View } from "react-native";

const SettingsDeleteUser = () => {
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the delete user settings page" />
        </View>
    );
};

export default SettingsDeleteUser;