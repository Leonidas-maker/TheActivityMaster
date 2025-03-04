import React, { useState, useEffect } from "react";
import { ScrollView, View, Keyboard, KeyboardAvoidingView, TouchableWithoutFeedback, useColorScheme, Platform, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getPrograms } from "@/src/services/club/programService";

const ClubManagePrograms = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const navigation = useNavigation();
    const { club_id } = useLocalSearchParams();

    useEffect(() => {
            const fetchPrograms = async () => {
                try {
                    //! Currently fixed to 50 prgrams (later will be changed to infinite scroll)
                    const data = await getPrograms(club_id, 1, 50);
                    console.log(data);
                } catch (error) {
                    console.error("Error during fetchPrograms call:", error);
                }
            }
            fetchPrograms();
        }, [club_id]);

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(program)/AddProgram?club_id=${club_id}`);
    };

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

export default ClubManagePrograms;