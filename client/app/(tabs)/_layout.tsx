import { Tabs } from 'expo-router';
import React, { useState, useEffect } from "react";
import { useColorScheme } from "react-native";
import ActiveDiscoverSGV from "../../public/images/navigatorIcons/active/ActiveDiscoverSVG";
import DiscoverSVG from "../../public/images/navigatorIcons/inactive/DiscoverSVG";
import ActiveOverviewSVG from "../../public/images/navigatorIcons/active/ActiveOverviewSVG";
import OverviewSVG from "../../public/images/navigatorIcons/inactive/OverviewSVG";
import ActiveCalendarSVG from "../../public/images/navigatorIcons/active/ActiveCalendarSVG";
import CalendarSVG from "../../public/images/navigatorIcons/inactive/CalendarSVG";

export default function TabLayout() {
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

    // Set the colors based on the color scheme
    const backgroundColor = isLight ? "#E8EBF7" : "#1E1E24";
    const headerTintColor = isLight ? "#171717" : "#E0E2DB";
    const tabBarActiveTintColor = isLight ? "#DE1A1A" : "#ED2A1D";
    const tabBarInactiveTintColor = isLight ? "#B71515" : "#C91818";

    return (
        <Tabs
            screenOptions={{
                headerShown: true,
                headerStyle: {
                    backgroundColor: backgroundColor,
                },
                tabBarStyle: { backgroundColor: backgroundColor },
                headerTintColor: headerTintColor,
                tabBarActiveTintColor: tabBarActiveTintColor,
                tabBarInactiveTintColor: tabBarInactiveTintColor,
            }}>
            <Tabs.Screen
                name="DiscoverHome"
                options={{
                    headerTitle: "TheActivityMaster",
                    tabBarLabel: "Entdecken",
                    tabBarIcon: ({ color, size, focused }) => {
                        if (focused) {
                            return (
                                <ActiveDiscoverSGV width={size} height={size} fill={color} />
                            );
                        } else {
                            return <DiscoverSVG width={size} height={size} fill={color} />;
                        }
                    },
                }}
            />
            <Tabs.Screen
                name="CalendarHome"
                options={{
                    headerTitle: "TheActivityMaster",
                    tabBarLabel: "Kalender",
                    headerShown: true,
                    tabBarIcon: ({ color, size, focused }) => {
                        if (focused) {
                            return (
                                <ActiveCalendarSVG width={size} height={size} fill={color} />
                            );
                        } else {
                            return <CalendarSVG width={size} height={size} fill={color} />;
                        }
                    },
                }}
            />
            {/* <Tabs.Screen
                name="Weiteres"
                options={{
                    headerTitle: "Weiteres",
                    headerShown: true,
                    tabBarIcon: ({ color, size, focused }) => {
                        if (focused) {
                            return (
                                <ActiveOverviewSVG width={size} height={size} fill={color} />
                            );
                        } else {
                            return <OverviewSVG width={size} height={size} fill={color} />;
                        }
                    },
                }}
            /> */}
        </Tabs>
    );
}