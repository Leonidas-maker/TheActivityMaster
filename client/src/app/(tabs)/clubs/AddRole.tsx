import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Alert, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { createProgram } from "@/src/services/club/programService";
import { getProgramCategories } from "@/src/services/club/programService";

const AddRole = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();

    // State to track if the theme is light
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
    };

    const handleInfoPress = () => {
        router.navigate("/(tabs)/clubs/InfoRole");
    };

    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: "auto", marginRight: 15 }}
                    />
                </Pressable>
            ),
            headerRight: () => (
                <Pressable onPress={handleInfoPress}>
                    <Icon
                        name="info"
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

export default AddRole;