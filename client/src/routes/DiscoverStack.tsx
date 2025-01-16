import React, { useEffect, useState } from 'react';
import { useColorScheme } from "react-native";
import { createStackNavigator } from '@react-navigation/stack';
import DiscoverHome from '../screens/discover/DiscoverHome';

const Stack = createStackNavigator();

const DiscoverStack: React.FC = () => {
    const [isLight, setIsLight] = useState(false);

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    // Get the current color scheme
    const colorScheme = useColorScheme();

    // Check if the color scheme is light or dark
    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    const backgroundColor = isLight ? "#E8EBF7" : "#1E1E24";
    const headerTintColor = isLight ? "#171717" : "#E0E2DB";

    return (
        <Stack.Navigator
            screenOptions={{
                headerStyle: {
                    backgroundColor: backgroundColor,
                },
                headerTintColor: headerTintColor,
            }}>
            <Stack.Screen name="DiscoverHome" component={DiscoverHome} />
        </Stack.Navigator>
    );
};

export default DiscoverStack;