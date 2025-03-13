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
import { asyncLoadData } from '@/src/services/asyncStorageService';
import { useAuth } from '@/src/provider/AuthContextProvider';
import ActiveClubSVG from '@/public/images/navigatorIcons/active/ActiveClubSVG';
import ClubSVG from '@/public/images/navigatorIcons/inactive/ClubSVG';
import ActiveSearchSVG from '@/public/images/navigatorIcons/active/ActiveSearchSVG';
import SearchSVG from '@/public/images/navigatorIcons/inactive/SearchSVG';

export default function TabLayout() {
    const [isLight, setIsLight] = useState(false);
    const { t } = useTranslation("router");

    const { authState } = useAuth();
    const { isLoggedIn, isVerified, isAdmin } = authState;

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
                key={`${isLoggedIn}-${isVerified}-${isAdmin}`} // This forces a remount when auth state changes
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
                    name="index"
                    options={{
                        headerTitle: "TheActivityMaster",
                        tabBarLabel: t("discover_tab"),
                        tabBarIcon: ({ color, size, focused }) =>
                            focused ? (
                                <ActiveDiscoverSGV width={size} height={size} fill={color} />
                            ) : (
                                <DiscoverSVG width={size} height={size} fill={color} />
                            ),
                    }}
                />
                <Tabs.Screen
                    name="CalendarHome"
                    options={{
                        headerTitle: "TheActivityMaster",
                        tabBarLabel: t("calendar_tab"),
                        headerShown: true,
                        tabBarIcon: ({ color, size, focused }) =>
                            focused ? (
                                <ActiveCalendarSVG width={size} height={size} fill={color} />
                            ) : (
                                <CalendarSVG width={size} height={size} fill={color} />
                            ),
                    }}
                />
                <Tabs.Screen
                    name="search"
                    options={{
                        headerTitle: t("search_tab"),
                        tabBarLabel: t("search_tab"),
                        headerShown: false,
                        tabBarIcon: ({ color, size, focused }) =>
                            focused ? (
                                <ActiveSearchSVG width={size} height={size} fill={color} />
                            ) : (
                                <SearchSVG width={size} height={size} fill={color} />
                            ),
                    }}
                />
                <Tabs.Screen
                    name="clubs"
                    options={{
                        headerTitle: t("clubs_tab"),
                        tabBarLabel: t("clubs_tab"),
                        headerShown: false,
                        tabBarItemStyle: {
                            display: isLoggedIn && (isVerified || isAdmin) ? "flex" : "none",
                        },
                        tabBarIcon: ({ color, size, focused }) =>
                            focused ? (
                                <ActiveClubSVG width={size} height={size} fill={color} />
                            ) : (
                                <ClubSVG width={size} height={size} fill={color} />
                            ),
                    }}
                />
                <Tabs.Screen
                    name="overview"
                    options={{
                        headerTitle: t("more_tab"),
                        tabBarLabel: t("more_tab"),
                        headerShown: false,
                        tabBarIcon: ({ color, size, focused }) =>
                            focused ? (
                                <ActiveOverviewSVG width={size} height={size} fill={color} />
                            ) : (
                                <OverviewSVG width={size} height={size} fill={color} />
                            ),
                    }}
                />
            </Tabs>
        </ThemeProvider>
    );
}