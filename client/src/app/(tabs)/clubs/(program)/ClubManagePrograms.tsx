import React, { useState, useEffect, useCallback } from "react";
import {
    ScrollView,
    View,
    Keyboard,
    KeyboardAvoidingView,
    TouchableWithoutFeedback,
    useColorScheme,
    Platform,
    Pressable,
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams, useFocusEffect } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getPrograms } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ClubManagePrograms = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const navigation = useNavigation();
    const { club_id } = useLocalSearchParams();

    // State for available programs
    const [programs, setPrograms] = useState<any[]>([]);

    useFocusEffect(
        useCallback(() => {
            const fetchPrograms = async () => {
                try {
                    //! Currently fixed to 50 programs (later will be changed to infinite scroll)
                    const data = await getPrograms(club_id, 1, 50);
                    setPrograms(data);
                } catch (error) {
                    Toast.show({
                        type: "error",
                        text1: "roleManageError",
                        text2: "roleManageErrorDescription",
                    });
                }
            };
            fetchPrograms();
        }, [club_id])
    );

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

    // Prepare arrays for the "All Programs" PageNavigator props
    const programNames = programs.map((program) => program.name);
    const onPressFunctions = programs.map((program) => () =>
        router.push(`/(tabs)/clubs/(program)/ManageProgram?club_id=${club_id}&program_id=${program.id}`)
    );
    // For the left icons we use a common icon for all programs, e.g., "event"
    const iconNames = programs.map(() => "event");

    // Prepare filtered arrays for each status
    const draftPrograms = programs.filter((program) => program.status === "draft");
    const activePrograms = programs.filter((program) => program.status === "active");
    const inactivePrograms = programs.filter((program) => program.status === "inactive");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            {programs.length > 0 ? (
                <>
                    {/* Active Programs Navigator (rendered only if there are active programs) */}
                    {activePrograms.length > 0 && (
                        <PageNavigator
                            title={t("activePrograms")}
                            texts={activePrograms.map((program) => program.name)}
                            onPressFunctions={activePrograms.map((program) => () =>
                                router.push(
                                    `/(tabs)/clubs/(program)/ManageProgram?club_id=${club_id}&program_id=${program.id}`
                                )
                            )}
                            iconNames={activePrograms.map(() => "event")}
                        />
                    )}

                    {/* Draft Programs Navigator (rendered only if there are draft programs) */}
                    {draftPrograms.length > 0 && (
                        <PageNavigator
                            title={t("draftPrograms")}
                            texts={draftPrograms.map((program) => program.name)}
                            onPressFunctions={draftPrograms.map((program) => () =>
                                router.push(
                                    `/(tabs)/clubs/(program)/ManageProgram?club_id=${club_id}&program_id=${program.id}`
                                )
                            )}
                            iconNames={draftPrograms.map(() => "event")}
                        />
                    )}

                    {/* Inactive Programs Navigator (rendered only if there are inactive programs) */}
                    {inactivePrograms.length > 0 && (
                        <PageNavigator
                            title={t("inactivePrograms")}
                            texts={inactivePrograms.map((program) => program.name)}
                            onPressFunctions={inactivePrograms.map((program) => () =>
                                router.push(
                                    `/(tabs)/clubs/(program)/ManageProgram?club_id=${club_id}&program_id=${program.id}`
                                )
                            )}
                            iconNames={inactivePrograms.map(() => "event")}
                        />
                    )}
                </>
            ) : (
                <View className="py-4">
                    <Heading text={t("noPrograms")} />
                </View>
            )}
            <DefaultToast />
        </ScrollView>
    );
};

export default ClubManagePrograms;
