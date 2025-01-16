import React, { useEffect, useState } from 'react';
import { useColorScheme } from "react-native";
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import BottomTabNavigator from './BottomTabNavigator';
import DiscoverStack from './DiscoverStack';
import OverviewStack from './OverviewStack';
import SettingsStack from './SettingsStack';
import CalendarStack from './CalendarStack';

const Stack = createStackNavigator();

const RootNavigator: React.FC = () => {
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
        <NavigationContainer>
            <Stack.Navigator
                screenOptions={{
                    headerStyle: {
                        backgroundColor: backgroundColor,
                    },
                    headerTintColor: headerTintColor,
                    headerBackButtonDisplayMode: "minimal",
                }}>
                <Stack.Screen
                    name="Tabs"
                    component={BottomTabNavigator}
                    options={{ headerShown: false }}
                />
                <Stack.Screen
                    name="Discover"
                    component={DiscoverStack}
                    options={{}}
                />
                <Stack.Screen
                    name="Overview"
                    component={OverviewStack}
                    options={{}}
                />
                <Stack.Screen
                    name="Settings"
                    component={SettingsStack}
                    options={{}}
                />
                <Stack.Screen
                    name="Calendar"
                    component={CalendarStack}
                    options={{}}
                />
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default RootNavigator;
