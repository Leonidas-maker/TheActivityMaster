import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Pressable } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams, useNavigation } from "expo-router";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Heading from "@/src/components/textFields/Heading";
import Toast from "react-native-toast-message";
import { getMembershipUsers } from "@/src/services/club/membershipService";
import Icon from "react-native-vector-icons/MaterialIcons";

const SubscriberOverview = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, membership_id } = useLocalSearchParams();
    const [subscribers, setSubscribers] = useState<string[]>([]);
    const colorScheme = useColorScheme();
    const isLight = colorScheme === "light";
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
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
        });
    }, [navigation, iconColor]);

    useEffect(() => {
        const fetchSubscribers = async () => {
            try {
                // Actual call to getSubscriptionUsers
                const data = await getMembershipUsers(club_id, membership_id);
                setSubscribers(data);
            } catch (error) {
                console.error("Error fetching subscribers", error);
            }
        };
        fetchSubscribers();
    }, []);

    const handleSubscriberPress = () => {
        Toast.show({
            type: "info",
            text1: t("subscriberClickedMessageText1"),
            text2: t("subscriberClickedMessageText2"),
        });
    };

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            {subscribers.length > 0 ? (
                <PageNavigator
                    title={t("subscriberOverviewTitle")}
                    texts={subscribers}
                    onPressFunctions={subscribers.map(() => handleSubscriberPress)}
                    iconNames={subscribers.map(() => "person")}
                />
            ) : (
                <View className="py-4">
                    <Heading text={t("noSubscribers")} />
                </View>
            )}
            <DefaultToast />
        </ScrollView>
    );
};

export default SubscriberOverview;