import React, { useState, useEffect, useCallback } from "react";
import { View, Text, Pressable, useColorScheme } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { asyncLoadData, asyncSaveData } from "@/src/services/asyncStorageService";
import { axiosInstance } from "@/src/services/api";
import { useFocusEffect, useRouter } from 'expo-router';
import { getUserData } from "@/src/services/user/userService";

const ProfileView = () => {
    const router = useRouter();

    const [isLight, setIsLight] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [wasLoggedIn, setWasLoggedIn] = useState(false);
    const [username, setUsername] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [isVerified, setIsVerified] = useState(false);

    useEffect(() => {
        async function checkLoginStatus() {
            const wasLoggedIn = await asyncLoadData("wasLoggedIn");
            if (wasLoggedIn === "true") {
                setWasLoggedIn(true);
            }
        }
        checkLoginStatus();
    }, []);

    // Function to check the login status and fetch the user data if user is logged in
    // So we can make sure that Username
    useFocusEffect(
        useCallback(() => {
            async function checkLoginStatus() {
                const isLoggedInData = await asyncLoadData("isLoggedIn");
                const loggedIn = isLoggedInData === "true";
                setIsLoggedIn(loggedIn);

                if (loggedIn) {
                    try {
                        const data = await getUserData();
                        setUsername(data.username);
                        setFirstName(data.first_name);
                        setLastName(data.last_name);
                        setIsVerified(data.identity_verified);
                        // Save verified status directly from data to avoid stale state issues
                        await asyncSaveData("isVerified", data.identity_verified.toString());
                    } catch (error) {
                        console.error("Error fetching user data:", error);
                    }
                }
            }
            checkLoginStatus();
        }, [isLoggedIn])
    );

    useEffect(() => {
        try {
            if (isLoggedIn) {
                getUserData().then((data) => {
                    setUsername(data.username);
                    setFirstName(data.first_name);
                    setLastName(data.last_name);
                });
            }
        } catch (error) {
            console.error("Error:", error);
        };
    }, [isLoggedIn]);

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

    // Set the icon color based on the color scheme
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleLoginPress = () => {
        if (wasLoggedIn) {
            router.navigate("/auth");
        } else {
            router.navigate("/auth/SignUp");
        }
    };

    const handleProfilePress = () => {
        router.navigate("/(tabs)/overview/(settings)/SettingsUser");
    };

    return (
        <View className="m-4">
            <Text className="text-black dark:text-white text-xl font-bold mb-2">
                Profil
            </Text>
            <View className="bg-light_secondary dark:bg-dark_secondary rounded-lg shadow-md p-4">
                {isLoggedIn ? (
                    <Pressable onPress={handleProfilePress} className="active:opacity-50">
                        <View className="flex-row justify-between items-center">
                            <Icon name="person" size={40} color={iconColor} />
                            <View className="ml-2">
                                <Text className="text-black dark:text-white font-bold text-2xl">
                                    {firstName} {lastName} {isVerified && <Icon name="verified" size={15} color={iconColor} />}
                                </Text>
                                <Text className="text-black dark:text-white font-bold text-xs">
                                    @{username}
                                </Text>
                            </View>
                            <Icon
                                name="arrow-forward-ios"
                                size={30}
                                color={iconColor}
                                style={{ marginLeft: "auto" }}
                            />
                        </View>
                    </Pressable>
                ) : (
                    <Pressable onPress={handleLoginPress} className="active:opacity-50">
                        <View className="flex-row justify-between items-center">
                            <Icon name="person" size={40} color={iconColor} />
                            <View className="ml-2">
                                <Text className="text-black dark:text-white font-bold text-3xl">
                                    {wasLoggedIn ? "Anmelden" : "Registrieren"}
                                </Text>
                            </View>
                            <Icon
                                name="arrow-forward-ios"
                                size={30}
                                color={iconColor}
                                style={{ marginLeft: "auto" }}
                            />
                        </View>
                    </Pressable>
                )}
            </View>
        </View>

    );
}

export default ProfileView;