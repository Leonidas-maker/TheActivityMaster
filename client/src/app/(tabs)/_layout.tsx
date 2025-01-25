import { Tabs } from 'expo-router';
import React, { useState, useEffect } from "react";
import { useTranslation } from 'react-i18next';
import { useColorScheme } from "nativewind";
import ActiveDiscoverSGV from "../../../public/images/navigatorIcons/active/ActiveDiscoverSVG";
import DiscoverSVG from "../../../public/images/navigatorIcons/inactive/DiscoverSVG";
import ActiveOverviewSVG from "../../../public/images/navigatorIcons/active/ActiveOverviewSVG";
import OverviewSVG from "../../../public/images/navigatorIcons/inactive/OverviewSVG";
import ActiveCalendarSVG from "../../../public/images/navigatorIcons/active/ActiveCalendarSVG";
import CalendarSVG from "../../../public/images/navigatorIcons/inactive/CalendarSVG";
import { ThemeProvider } from "@/src/provider/ThemeProvider";

export default function TabLayout() {
    const [isLight, setIsLight] = useState(false);
    const { t } = useTranslation("router");

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    // Get the current color scheme
    const { colorScheme } = useColorScheme();


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
        <ThemeProvider>
            <Tabs
                backBehavior='history'
                screenOptions={{
                    headerShown: true,
                    headerStyle: {
                        backgroundColor: backgroundColor,
                    },
                    tabBarStyle: { backgroundColor: backgroundColor },
                    headerTintColor: headerTintColor,
                    tabBarActiveTintColor: tabBarActiveTintColor,
                    tabBarInactiveTintColor: tabBarInactiveTintColor,
                }}
            >
                <Tabs.Screen
                    name="index" // aka DiscoverHome
                    options={{
                        lazy: true,
                        headerTitle: "TheActivityMaster",
                        tabBarLabel: t("discover_tab"),
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
                        lazy: true,
                        headerTitle: "TheActivityMaster",
                        tabBarLabel: t("calendar_tab"),
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
                <Tabs.Screen
                    name="OverviewHome"
                    options={{
                        lazy: true,
                        headerTitle: t("more_tab"),
                        tabBarLabel: t("more_tab"),
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
                />
            </Tabs>
        </ThemeProvider>
    );
}