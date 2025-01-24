import { Stack, router, useLocalSearchParams } from 'expo-router';
import React, { useState, useEffect } from "react";
import { useColorScheme, TouchableOpacity, Text } from "react-native";

export default function SettingsLayout() {
    const [isLight, setIsLight] = useState(false);

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    const colorScheme = useColorScheme();

    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    const backgroundColor = isLight ? "#E8EBF7" : "#1E1E24";
    const headerTintColor = isLight ? "#171717" : "#E0E2DB";

    // Verwende useLocalSearchParams für übergebene Parameter
    const { previousRoute } = useLocalSearchParams();

    return (
        <Stack
            screenOptions={{
                headerTitle: "Einstellungen",
                headerStyle: {
                    backgroundColor: backgroundColor,
                },
                headerTintColor: headerTintColor
            }}
        />
    );
}

export const unstable_settings = {
    initialRouteName: 'index',
};