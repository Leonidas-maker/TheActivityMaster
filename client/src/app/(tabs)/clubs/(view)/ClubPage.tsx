import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getClub } from "@/src/services/club/clubService";
import { getMemberships } from "@/src/services/club/membershipService";
import { getPrograms } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

const ClubPage = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const { club_id } = useLocalSearchParams();

    const [clubData, setClubData] = useState<any>(null);
    const [programs, setPrograms] = useState<any[]>([]);
    const [memberships, setMemberships] = useState<any[]>([]);
    const [loadingClub, setLoadingClub] = useState<boolean>(true);
    const [loadingPrograms, setLoadingPrograms] = useState<boolean>(true);
    const [loadingMemberships, setLoadingMemberships] = useState<boolean>(true);

    // Create shared values and refs for pagination
    const progressPrograms = useSharedValue(0);
    const progressMemberships = useSharedValue(0);
    const refPrograms = useRef<ICarouselInstance>(null);
    const refMemberships = useRef<ICarouselInstance>(null);

    // Use color scheme to set pagination colors
    const colorScheme = useColorScheme();
    const dotStyle = {
        width: 10,
        height: 4,
        backgroundColor: colorScheme === "dark" ? "#cccccc" : "#444444",
    };
    const activeDotStyle = {
        overflow: "hidden" as "hidden",
        backgroundColor: colorScheme === "dark" ? "#ED2A1D" : "#DE1A1A",
    };
    const containerStyle = {
        gap: 5,
    };

    useEffect(() => {
        // Fetch club details
        getClub(club_id)
            .then((data) => setClubData(data))
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
            })
            .finally(() => setLoadingClub(false));

        // Fetch programs (fixed to 50 programs)
        getPrograms(club_id, 1, 50)
            .then((data) => setPrograms(data))
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
            })
            .finally(() => setLoadingPrograms(false));

        // Fetch memberships
        getMemberships(club_id)
            .then((data) => setMemberships(data))
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("inputError_text"),
                    text2: t("inputError_subtext"),
                });
            })
            .finally(() => setLoadingMemberships(false));
    }, [club_id, t]);

    const screenWidth = Dimensions.get("window").width;

    const truncate = (text: string, maxLength: number) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + "...";
    };

    return (
        <ScrollView className="bg-light_primary dark:bg-dark_primary">
            <View className="p-4">
                {/* Club Information */}
                {loadingClub ? (
                    <ActivityIndicator size="large" color="#000" />
                ) : (
                    <View>
                        {/* Club Picture Placeholder */}
                        <View className="w-full h-52 bg-gray-300 dark:bg-gray-700 justify-center items-center mb-4 rounded-xl">
                            <DefaultText text={t("clubPicturePlaceholder")} />
                        </View>
                        <Heading text={clubData?.name || ""} />
                        <DefaultText text={truncate(clubData?.description || "", 100)} />
                        <DefaultText text={`${clubData?.address?.street}, ${clubData?.address?.city}, ${clubData?.address?.state}, ${clubData?.address?.postal_code}, ${clubData?.address?.country}`} />
                        <View className="mt-2">
                            <DefaultText text={t("ownersLabel")} />
                            {clubData?.owners?.map((owner: any, index: number) => (
                                <DefaultText key={index} text={`${owner.first_name} ${owner.last_name} (${owner.email})`} />
                            ))}
                        </View>
                    </View>
                )}

                {/* Programs Carousel */}
                <View className="mt-8">
                    <Heading text={t("programsTitle")} />
                    {loadingPrograms ? (
                        <ActivityIndicator size="large" color="#000" />
                    ) : programs.length === 0 ? (
                        <DefaultText text={t("noProgramsAvailable")} />
                    ) : (
                        <>
                            <Carousel
                                ref={refPrograms}
                                width={screenWidth * 0.9}
                                height={200}
                                data={programs}
                                scrollAnimationDuration={1000}
                                mode="parallax"
                                modeConfig={{
                                    parallaxScrollingScale: 0.9,
                                    parallaxScrollingOffset: 50,
                                }}
                                onProgressChange={progressPrograms}
                                renderItem={({ item, index }) => (
                                    <TouchableOpacity
                                        key={index}
                                        onPress={() => router.navigate("/")}
                                        className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                                    >
                                        {/* Program Picture Placeholder */}
                                        <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                                            <DefaultText text={t("programPicturePlaceholder")} />
                                        </View>
                                        <DefaultText text={item.name} />
                                        <DefaultText text={truncate(item.description, 50)} />
                                        {item.price > 0 ? (
                                            <DefaultText text={t("priceLabel", { price: `€${(item.price / 100).toFixed(2)}` })} />
                                        ) : (
                                            <DefaultText text={t("pricingPerSession")} />
                                        )}
                                    </TouchableOpacity>
                                )}
                            />
                            <Pagination.Basic<{ color: string }>
                                progress={progressPrograms}
                                data={programs}
                                dotStyle={dotStyle}
                                activeDotStyle={activeDotStyle}
                                containerStyle={containerStyle}
                                horizontal
                                onPress={(index) => {
                                    refPrograms.current?.scrollTo({ count: index - progressPrograms.value, animated: true });
                                }}
                            />
                        </>
                    )}
                </View>

                {/* Memberships Carousel */}
                <View className="mt-8 mb-8">
                    <Heading text={t("membershipsTitle")} />
                    {loadingMemberships ? (
                        <ActivityIndicator size="large" color="#000" />
                    ) : memberships.length === 0 ? (
                        <DefaultText text={t("noMembershipsAvailable")} />
                    ) : (
                        <>
                            <Carousel
                                ref={refMemberships}
                                width={screenWidth * 0.9}
                                height={200}
                                data={memberships}
                                scrollAnimationDuration={1000}
                                mode="parallax"
                                modeConfig={{
                                    parallaxScrollingScale: 0.9,
                                    parallaxScrollingOffset: 50,
                                }}
                                onProgressChange={progressMemberships}
                                renderItem={({ item, index }) => (
                                    <TouchableOpacity
                                        key={index}
                                        onPress={() => router.navigate("/")}
                                        className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                                    >
                                        {/* Membership Picture Placeholder */}
                                        <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                                            <DefaultText text={t("membershipPicturePlaceholder")} />
                                        </View>
                                        <DefaultText text={item.name} />
                                        <DefaultText text={truncate(item.description, 50)} />
                                        <DefaultText text={t("priceLabel", { price: `€${(item.price / 100).toFixed(2)}` })} />
                                        <DefaultText text={t("durationLabel", { duration: item.duration, durationUnit: item.duration_unit })} />
                                    </TouchableOpacity>
                                )}
                            />
                            <Pagination.Basic<{ color: string }>
                                progress={progressMemberships}
                                data={memberships}
                                dotStyle={dotStyle}
                                activeDotStyle={activeDotStyle}
                                containerStyle={containerStyle}
                                horizontal
                                onPress={(index) => {
                                    refMemberships.current?.scrollTo({ count: index - progressMemberships.value, animated: true });
                                }}
                            />
                        </>
                    )}
                </View>
            </View>
            <DefaultToast />
        </ScrollView>
    );
};

export default ClubPage;