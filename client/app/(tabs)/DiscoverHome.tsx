import React from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";

export default function Tab() {
    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text="Welcome to Discover" />
        </View>
    );
};