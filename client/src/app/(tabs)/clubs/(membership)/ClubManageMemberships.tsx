import React, { useState, useEffect, useCallback } from "react";
import { ScrollView, View, Pressable, useColorScheme } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams, useFocusEffect } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getMemberships } from "@/src/services/club/membershipService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Heading from "@/src/components/textFields/Heading";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

const ClubManageMemberships = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const navigation = useNavigation();
    const { club_id } = useLocalSearchParams();
    const colorScheme = useColorScheme();
    const isLight = colorScheme === "light";
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const [memberships, setMemberships] = useState<any[]>([]);

    useFocusEffect(
        useCallback(() => {
            const fetchMemberships = async () => {
                try {
                    const data = await getMemberships(club_id);
                    setMemberships(data);
                } catch (error) {
                    Toast.show({
                        type: "error",
                        text1: t("roleManageError"),
                        text2: t("roleManageErrorDescription"),
                    });
                }
            };
            fetchMemberships();
        }, [club_id, t])
    );

    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(membership)/AddMembership?club_id=${club_id}`);
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

    // Filter memberships by status
    const draftMemberships = memberships.filter(
        (membership) => membership.status === "draft"
    );
    const bookableMemberships = memberships.filter(
        (membership) => membership.status === "bookable"
    );
    const notBookableMemberships = memberships.filter(
        (membership) => membership.status === "not_bookable"
    );

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            {memberships.length > 0 ? (
                <>
                    {draftMemberships.length > 0 && (
                        <PageNavigator
                            title={t("draftMemberships")}
                            texts={draftMemberships.map((membership) => membership.name)}
                            onPressFunctions={draftMemberships.map((membership) => () =>
                                router.push(`/(tabs)/clubs/(membership)/ManageMembership?club_id=${club_id}&membership_id=${membership.id}`)
                            )}
                            iconNames={draftMemberships.map(() => "event")}
                        />
                    )}
                    {bookableMemberships.length > 0 && (
                        <PageNavigator
                            title={t("bookableMemberships")}
                            texts={bookableMemberships.map((membership) => membership.name)}
                            onPressFunctions={bookableMemberships.map((membership) => () =>
                                router.push(`/(tabs)/clubs/(membership)/ManageMembership?club_id=${club_id}&membership_id=${membership.id}`)
                            )}
                            iconNames={bookableMemberships.map(() => "event")}
                        />
                    )}
                    {notBookableMemberships.length > 0 && (
                        <PageNavigator
                            title={t("notBookableMemberships")}
                            texts={notBookableMemberships.map((membership) => membership.name)}
                            onPressFunctions={notBookableMemberships.map((membership) => () =>
                                router.push(`/(tabs)/clubs/(membership)/ManageMembership?club_id=${club_id}&membership_id=${membership.id}`)
                            )}
                            iconNames={notBookableMemberships.map(() => "event")}
                        />
                    )}
                </>
            ) : (
                <View className="py-4">
                    <Heading text={t("noMemberships")} />
                </View>
            )}
            <DefaultToast />
        </ScrollView>
    );
};

export default ClubManageMemberships;