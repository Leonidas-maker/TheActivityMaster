import DefaultText from "@/src/components/textFields/DefaultText";
import React from "react";
import { View } from "react-native";

const SettingsNotifications = () => {
    //TODO: Implement settings notifications page
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the notifications settings page" />
        </View>
    );
};

export default SettingsNotifications;