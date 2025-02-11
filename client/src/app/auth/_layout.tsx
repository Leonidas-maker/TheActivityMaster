import { Stack, router } from 'expo-router';
import React, { useEffect, useState } from "react";
import { useColorScheme } from "nativewind";
import { useTranslation } from "react-i18next";
import { useNavigation, useRouter } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { SafeAreaProvider } from "react-native-safe-area-context";

export default function AuthLayout() {
    const [isLight, setIsLight] = useState(false);
    const { t } = useTranslation("router");
    const navigation = useNavigation();
    const router = useRouter();

    const { colorScheme } = useColorScheme();

    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    const backgroundColor = isLight ? "#E8EBF7" : "#1E1E24";
    const headerTintColor = isLight ? "#171717" : "#E0E2DB";
    // Set the icon color based on the color scheme
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleBackPress = () => {
        if (navigation.canGoBack()) {
            navigation.goBack();
        } else {
            router.push("/(tabs)");
        }
    };

    return (
        <SafeAreaProvider>
            <Stack
                screenOptions={{
                    headerShown: true,
                    headerStyle: {
                        backgroundColor: backgroundColor,
                    },
                    headerTintColor: headerTintColor,
                    headerLeft: () => (
                        <Icon
                            name="close"
                            size={30}
                            color={iconColor}
                            onPress={handleBackPress}
                        />
                    ),
                    gestureEnabled: false
                }}
            >
                <Stack.Screen
                    name="index"
                    options={{
                        headerTitle: t("login_header"),
                    }}
                />
                <Stack.Screen
                    name="SignUp"
                    options={{
                        headerTitle: t("register_header"),
                    }}
                />
                <Stack.Screen
                    name="(info)/VerifyMail"
                    options={{
                        headerTitle: t("register_header"),
                    }}
                />
                <Stack.Screen
                    name="(info)/Terms"
                    options={{
                        headerShown: false,
                        presentation: "modal",
                    }}
                />
                <Stack.Screen
                    name="SignInVerify"
                    options={{
                        headerTitle: t("loginVerfiy_header"),
                    }}
                />
            </Stack>
        </SafeAreaProvider>
    );
}
