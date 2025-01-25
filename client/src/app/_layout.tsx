import "../../global.css";
import { Stack } from "expo-router";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { ThemeProvider } from "../provider/ThemeProvider";
import { useState, useEffect } from "react";
import { useColorScheme } from "nativewind";
import { useTranslation } from "react-i18next";

import "../custom_logger/custom_logger";
import "../locales/i18n";

// SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
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

  return (
    <ThemeProvider>
      <GestureHandlerRootView>
        <SafeAreaProvider>
          <StatusBar style="auto" />
          <Stack
            initialRouteName="(tabs)"
            screenOptions={{
              headerShown: true,
              headerStyle: {
                backgroundColor: backgroundColor,
              },
              headerTintColor: headerTintColor,
            }}
          >
            {/* Tabs-Navigation */}
            <Stack.Screen name="(tabs)" options={{ headerShown: false }} />

            {/* Zusätzliche Screens */}
            <Stack.Screen
              name="Settings"
              options={{
                headerBackTitle: t("back_btn"),
                headerShown: true,
                headerTitle: t("settings_header"),
              }}

            />
          </Stack>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ThemeProvider>
  );
}

