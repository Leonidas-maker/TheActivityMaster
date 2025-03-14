import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme, Text } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { getMembership } from "@/src/services/club/membershipService";
import { getPrograms } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Subheading from "@/src/components/textFields/Subheading";
import { getUserMemberships } from "@/src/services/user/userService";

const MembershipPageGlobal = ({ club_id, membership_id, route_name }: { club_id: string | string[], membership_id: string | string[], route_name: string | string[] }) => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    // States for membership details and program details
    const [membershipData, setMembershipData] = useState<any>(null);
    const [programs, setPrograms] = useState<any[]>([]);
    const [loadingMembership, setLoadingMembership] = useState<boolean>(true);
    const [loadingPrograms, setLoadingPrograms] = useState<boolean>(true);
    const [userMemberships, setUserMemberships] = useState<any[]>([]);

    // Get screen width for carousel sizing
    const screenWidth = Dimensions.get("window").width;
    const colorScheme = useColorScheme();
    const dotStyle = { width: 10, height: 4, backgroundColor: colorScheme === "dark" ? "#cccccc" : "#444444" };
    const activeDotStyle = { overflow: "hidden" as "hidden", backgroundColor: colorScheme === "dark" ? "#ED2A1D" : "#DE1A1A" };
    const containerStyle = { gap: 5 };

    // Shared value and ref for the programs carousel
    const progressPrograms = useSharedValue(0);
    const refPrograms = useRef<ICarouselInstance>(null);

    useEffect(() => {
        // Fetch membership details using getMembership
        getMembership(club_id, membership_id)
            .then((data) => setMembershipData(data))
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription"),
                });
            })
            .finally(() => setLoadingMembership(false));

        // Fetch programs for additional program details
        getPrograms(club_id, 1, 50)
            .then((data) => setPrograms(data))
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription"),
                });
            })
            .finally(() => setLoadingPrograms(false));
    }, [club_id, membership_id, t]);

    useEffect(() => {
        getUserMemberships()
            .then((data) => setUserMemberships(data))
            .catch((error) => {
                console.error('Error fetching user memberships', error);
            });
    }, []);

    const alreadyBooked = membershipData ? userMemberships.some((um: any) => um.membership.id === membershipData.id) : false;

    return (
        <View style={{ flex: 1 }}>
            <ScrollView
                className="bg-light_primary dark:bg-dark_primary"
            >
                <View className="p-4">
                    {/* Membership Information */}
                    {loadingMembership ? (
                        <ActivityIndicator size="large" color="#000" />
                    ) : (
                        <View>
                            {/* Membership Picture Placeholder styled like ClubPageGlobal */}
                            <View className="w-full h-52 bg-gray-300 dark:bg-gray-700 justify-center items-center mb-4 rounded-xl">
                                <DefaultText text={t("membershipPicturePlaceholder")} />
                            </View>
                            <Heading text={membershipData?.name || ""} />
                            <Subheading text={t("membership_details")} />
                            <View className="py-2">
                                <DefaultText text={membershipData?.description || ""} />
                            </View>
                            <View className="py-2">
                                <DefaultText text={t("priceLabel", { price: `€${(membershipData?.price / 100).toFixed(2)}` })} />
                            </View>
                            <View className="py-2">
                                <DefaultText text={t("durationLabel", { duration: membershipData?.duration, durationUnit: membershipData?.duration_unit })} />
                            </View>
                        </View>
                    )}

                    {/* Programs Access Carousel */}
                    <View className="mt-8">
                        <Heading text={t("programsAccessTitle")} />
                        {loadingPrograms ? (
                            <ActivityIndicator size="large" color="#000" />
                        ) : (membershipData?.programs_access?.length ?? 0) === 0 ? (
                            <Subheading text={t("noProgramsAvailable")} />
                        ) : (
                            <>
                                <Carousel
                                    ref={refPrograms}
                                    width={screenWidth * 0.9}
                                    height={170}
                                    data={membershipData.programs_access}
                                    scrollAnimationDuration={1000}
                                    mode="parallax"
                                    modeConfig={{
                                        parallaxScrollingScale: 0.9,
                                        parallaxScrollingOffset: 50,
                                    }}
                                    onProgressChange={progressPrograms}
                                    renderItem={({ item, index }: { item: { program_id: string; additional_fee: number; membership_id: string }, index: number }) => {
                                        const programDetail = programs.find((p) => p.id === item.program_id);
                                        const programName = programDetail ? programDetail.name : t("programNameUnavailable");
                                        const feeText = item.additional_fee === 0
                                            ? t("program_free")
                                            : t("priceLabelFee", { price: `€${(item.additional_fee / 100).toFixed(2)}` });
                                        return (
                                            <TouchableOpacity
                                                key={index}
                                                // @ts-ignore
                                                onPress={() => router.navigate(`/(tabs)/${route_name}/(view)/ProgramPage?club_id=${club_id}&program_id=${item.program_id}`)}
                                                className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                                            >
                                                <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                                                    <DefaultText text={t("programPicturePlaceholder")} />
                                                </View>
                                                <DefaultText text={programName} />
                                                <DefaultText text={feeText} />
                                            </TouchableOpacity>
                                        );
                                    }}
                                />
                                <Pagination.Basic<{ color: string }>
                                    progress={progressPrograms}
                                    data={membershipData.programs_access}
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
                </View>
                {membershipData && (
                    <TouchableOpacity
                        // @ts-ignore
                        onPress={() => { if (!alreadyBooked) router.navigate(`/(tabs)/${route_name}/(view)/BookingPage?club_id=${club_id}&is_membership=true&membership_id=${membership_id}&price=${membershipData.price}&name=${membershipData.name}`); 
                        }}
                        disabled={alreadyBooked}
                        className={`mx-4 mb-4 p-4 rounded-xl items-center justify-center ${alreadyBooked ? 'bg-gray-400' : (colorScheme === 'dark' ? 'bg-white' : 'bg-black')
                            }`}
                    >
                        <Text className={alreadyBooked ? 'text-gray-600' : (colorScheme === 'dark' ? 'text-black' : 'text-white')}>
                            {alreadyBooked ? 'Already booked' : `Book for €${(membershipData.price / 100).toFixed(2)}`}
                        </Text>
                    </TouchableOpacity>
                )}
                <DefaultToast />
            </ScrollView>
        </View>
    );
};

export default MembershipPageGlobal;