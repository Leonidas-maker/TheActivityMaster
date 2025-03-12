import React, { useState, useEffect, useCallback } from "react";
import { ScrollView, View, useColorScheme, Pressable } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useFocusEffect, useNavigation } from "expo-router";
import { getMembership } from "@/src/services/club/membershipService";
import Heading from "@/src/components/textFields/Heading";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getProgram } from "@/src/services/club/programService";

const MembershipAccessOverview = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const navigation = useNavigation();
    const { club_id, membership_id } = useLocalSearchParams();
    const colorScheme = useColorScheme();
    const isLight = colorScheme === "light";
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // Declare state inside the component
    const [membership, setMembership] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [programsMap, setProgramsMap] = useState<{ [key: string]: any }>({});

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(membership)/AddProgramMembershipAccess?club_id=${club_id}&membership_id=${membership_id}`);
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

    useFocusEffect(
        useCallback(() => {
            const fetchMembership = async () => {
                try {
                    const data = await getMembership(club_id, membership_id);
                    setMembership(data);
                } catch (error) {
                    Toast.show({
                        type: "error",
                        text1: t("roleManageError"),
                        text2: t("roleManageErrorDescription"),
                    });
                } finally {
                    setLoading(false);
                }
            };
            fetchMembership();
        }, [club_id, membership_id, t])
    );

    useEffect(() => {
        if (membership && membership.programs_access) {
            const uniqueProgramIds = Array.from(
                new Set(membership.programs_access.map((access: any) => access.program_id as string))
            );
            Promise.all(
                uniqueProgramIds.map(async (programId) => {
                    try {
                        // Cast club_id to string to ensure proper types
                        const program = await getProgram(String(club_id), programId as string);
                        return { programId, program };
                    } catch (error) {
                        console.error("Error fetching program", programId, error);
                        return { programId, program: null };
                    }
                })
            ).then((results) => {
                const newMap: { [key: string]: any } = {};
                results.forEach(({ programId, program }) => {
                    newMap[programId as string] = program;
                });
                setProgramsMap(newMap);
            });
        }
    }, [membership, club_id]);

    if (loading) {
        return null;
    }

    const programsAccess = membership.programs_access || [];

    const accessItemsTexts = programsAccess.map((access: any) => {
        const program = programsMap[access.program_id as string];
        const programName = program ? program.name : "Loading...";
        return `${programName}`;
    });

    const accessOnPressFunctions = programsAccess.map((access: any) => {
        return () => {
            const encodedAccess = encodeURIComponent(JSON.stringify(access));
            router.push(
                `/(tabs)/clubs/(membership)/ManageProgramMembershipAccess?club_id=${club_id}&membership_id=${membership_id}&program_access=${encodedAccess}`
            );
        };
    });

    const accessIconNames = programsAccess.map(() => "settings");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                {programsAccess.length > 0 ? (
                    <PageNavigator
                        title={t("programAccessOverview")}
                        texts={accessItemsTexts}
                        onPressFunctions={accessOnPressFunctions}
                        iconNames={accessIconNames}
                    />
                ) : (
                    <View className="py-4">
                        <Heading text={t("noProgramAccess")} />
                    </View>
                )}
            <DefaultToast />
        </ScrollView>
    );
};

export default MembershipAccessOverview;