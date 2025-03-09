import React, { useEffect, useState } from "react";
import { ScrollView, View, useColorScheme, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getSessions } from "@/src/services/club/programSessionService";

const ClubManageSessions = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, program_id } = useLocalSearchParams();

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(session)/AddSession?club_id=${club_id}&program_id=${program_id}`);
    };

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const sessions = await getSessions(club_id, program_id);
                console.log(sessions);
            } catch (error) {
                console.error("Error during fetchSessions call:", error);
            }
        };
        fetchSessions();
    }, [club_id, program_id]);

    useEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                <Pressable onPress={handleAddPress}>
                    <Icon
                        name="add"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="items-center">
                <Heading text={t("createClub")} />
                <DefaultTextFieldInput placeholder={t("clubName")} />
                <DefaultTextFieldInput placeholder={t("clubDescription")} />
                <DefaultButton text={t("create")} />
            </View>
        </ScrollView>
    );
}

export default ClubManageSessions;