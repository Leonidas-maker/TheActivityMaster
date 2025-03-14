import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme, Text } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import { getProgram } from "@/src/services/club/programService";
import { getSessions } from "@/src/services/club/programSessionService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { getUserSessions } from "@/src/services/user/userService";
import { getUserMemberships } from '../../services/user/userService';
import { getMembership } from "@/src/services/club/membershipService";
import { useAuth } from '@/src/provider/AuthContextProvider';

// Define interfaces similar to EventPageGlobal
interface Session {
    session_type: string;
    capacity: number;
    price: number;
    start_datetime?: string;
    end_datetime?: string;
    day_of_week: string;
    start_time: string;
    end_time: string;
    start_date?: string;
    end_date?: string;
    address?: {
        street: string;
        postal_code: string;
        city: string;
        state: string;
        country: string;
    };
    id: string;
    program_id: string;
    occurrences?: Occurrence[];
}

interface MembershipResponse {
    name: string;
    description: string;
    price: number;
    currency: string;
    duration: number;
    duration_unit: string;
    id: string;
    club_id: string;
    status: string;
    programs_access: { program_id: string; additional_fee: number; membership_id: string }[];
}

interface Occurrence {
    id: string;
    session_id: string;
    status: string;
    occurrence_date: string;
    start_datetime: string;
    end_datetime: string;
    note: string;
}

interface ProgramResponse {
    name: string;
    description: string;
    price: number;
    currency: string;
    pricing_model: string; // 'package' or 'per_session'
    capacity: number;
    membership_required: boolean;
    club_id: string;
    id: string;
    categories: { id: string; name: string }[];
    status: string;
    sessions: Session[];
    membership_ids: string[];
}

// Helper functions to format date and time
const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
};

const formatTime = (timeString: string | undefined) => {
    if (!timeString) return "";

    // If the time string does not contain a 'T', assume it's a time-only string
    if (timeString.indexOf('T') === -1) {
        const parts = timeString.split(':');
        if (parts.length >= 2) {
            return `${parts[0]}:${parts[1]}`;
        }
        return "";
    } else {
        const date = new Date(timeString);
        if (isNaN(date.getTime())) {
            return "";
        }
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
};

// Helper function to render address
const renderAddress = (address: Session['address']) => {
    if (!address) return null;
    return (
        <DefaultText text={`${address.street}, ${address.city}, ${address.state}, ${address.postal_code}, ${address.country}`} />
    );
};

interface CoursePageGlobalProps {
    club_id: string | string[];
    program_id: string | string[];
    session_id: string | string[];
    pricing_model: string | string[];
    route_name: string | string[];
}

const CoursePageGlobal = ({ club_id, program_id, session_id, pricing_model, route_name }: CoursePageGlobalProps) => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    const colorScheme = useColorScheme();
    const screenWidth = Dimensions.get("window").width;

    const { authState } = useAuth();
    const { isLoggedIn } = authState;

    // States for session and program data
    const [sessionData, setSessionData] = useState<Session | null>(null);
    const [programData, setProgramData] = useState<ProgramResponse | null>(null);
    const [loadingSession, setLoadingSession] = useState<boolean>(true);
    const [loadingProgram, setLoadingProgram] = useState<boolean>(true);
    const [userSessions, setUserSessions] = useState<any[]>([]);
    const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);

    // Shared values and refs for carousels
    const progressProgram = useSharedValue(0);
    const refProgram = useRef<ICarouselInstance>(null);
    const progressOccurrences = useSharedValue(0);
    const refOccurrences = useRef<ICarouselInstance>(null);

    const [membershipDetails, setMembershipDetails] = useState<MembershipResponse[]>([]);
    const [loadingMemberships, setLoadingMemberships] = useState<boolean>(false);

    // Dot styles for pagination
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

    // Fetch session data based on session_id
    useEffect(() => {
        getSessions(club_id, program_id)
            .then((data: Session[]) => {
                const session = data.find((s) => s.id === session_id);
                if (session) {
                    setSessionData(session);
                } else {
                    Toast.show({
                        type: "error",
                        text1: t("courseNotFound"),
                        text2: t("courseNotFoundDesc"),
                    });
                }
            })
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription"),
                });
            })
            .finally(() => setLoadingSession(false));
    }, [club_id, program_id, session_id, t]);

    // Fetch program details for the carousel
    useEffect(() => {
        getProgram(club_id, program_id)
            .then((data: ProgramResponse) => {
                setProgramData(data);
                if (data.membership_ids && data.membership_ids.length > 0) {
                    setLoadingMemberships(true);
                    Promise.all(
                        data.membership_ids.map((membershipId) => getMembership(club_id, membershipId))
                    )
                        .then((memberships: MembershipResponse[]) => {
                            setMembershipDetails(memberships);
                        })
                        .catch(() => {
                            Toast.show({
                                type: "error",
                                text1: t("roleManageError"),
                                text2: t("roleManageErrorDescription"),
                            });
                        })
                        .finally(() => setLoadingMemberships(false));
                }
            })
            .catch(() => {
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription"),
                });
            })
            .finally(() => setLoadingProgram(false));
    }, [club_id, program_id, t]);

    useEffect(() => {
        getUserSessions()
            .then((data) => {
                setUserSessions(data);
            })
            .catch((error) => {
                console.error("Error fetching user sessions", error);
            });
    }, []);

    useEffect(() => {
        if (programData && programData.membership_ids.length > 0 && membershipDetails.length > 0) {
            getUserMemberships()
                .then((userMemberships) => {
                    for (const userMembership of userMemberships) {
                        const userMembershipId = userMembership.membership.id;
                        if (programData.membership_ids.includes(userMembershipId)) {
                            const membershipDetail = membershipDetails.find(m => m.id === userMembershipId);
                            if (membershipDetail) {
                                const access = membershipDetail.programs_access.find(access => access.program_id === programData.id);
                                if (access) {
                                    setProgramData({ ...programData, price: access.additional_fee });
                                    break;
                                }
                            }
                        }
                    }
                })
                .catch((error) => {
                    console.error("Error fetching user memberships", error);
                });
        }
    }, [programData, membershipDetails]);

    // Convert the provided session_id(s) to an array of strings
    const sessionIds = Array.isArray(session_id)
        ? session_id.map(String)
        : [String(session_id)];

    // Flatten the sessions from all courses in userSessions, handling any cases where sessions might be undefined
    const allUserSessionIds = userSessions.flatMap((course: any) =>
        course.sessions ? course.sessions.map((s: any) => String(s.id)) : []
    );

    // Determine if any of the provided sessionIds match one of the user session ids
    const alreadyBooked = sessionIds.some((id) => allUserSessionIds.includes(id));

    // Handler for navigating to program details
    const handleProgramPress = () => {
        // @ts-ignore
        router.navigate(`/(tabs)/${route_name}/(view)/ProgramPage?club_id=${club_id}&program_id=${programData?.id}`);
    };

    return (
        <>
            <ScrollView
                className="bg-light_primary dark:bg-dark_primary"
            >
                <View className="p-4">
                    {/* Program Picture Placeholder */}
                    <View className="w-full h-52 bg-gray-300 dark:bg-gray-700 justify-center items-center mb-4 rounded-xl">
                        <DefaultText text={t("programPicturePlaceholder")} />
                    </View>

                    {/* Session Details */}
                    {loadingSession ? (
                        <ActivityIndicator size="large" color="#000" />
                    ) : sessionData ? (
                        <View>
                            <Heading text={t("courseDetails")} />
                            <View className="py-2">
                                <DefaultText text={`${t("sessionType")}: ${t("session_type." + sessionData.session_type)}`} />
                                {pricing_model === "per_session" && (
                                    <>
                                        <DefaultText text={t("priceLabel", { price: `€${(sessionData.price / 100).toFixed(2)}` })} />
                                        <DefaultText text={t("capacityLabel", { capacity: sessionData.capacity })} />
                                    </>
                                )}
                                <DefaultText text={`${t("dayOfWeek")}: ${t("dayOfWeek." + sessionData.day_of_week)}`} />
                                <DefaultText text={`${t("start_time")}: ${formatTime(sessionData.start_time)}`} />
                                <DefaultText text={`${t("end_time")}: ${formatTime(sessionData.end_time)}`} />
                                {sessionData.start_date && (
                                    sessionData.end_date ? (
                                        <>
                                            <DefaultText text={`${t("start_date")}: ${formatDate(sessionData.start_date)}`} />
                                            <DefaultText text={`${t("end_date")}: ${formatDate(sessionData.end_date)}`} />
                                        </>
                                    ) : (
                                        <DefaultText text={t("dateSingle", { date: formatDate(sessionData.start_date) })} />
                                    )
                                )}
                                {sessionData.address && renderAddress(sessionData.address)}
                            </View>
                        </View>
                    ) : null}

                    {/* Occurrences Carousel */}
                    {sessionData && sessionData.occurrences && sessionData.occurrences.length > 0 && (
                        <View className="mt-4 mb-8">
                            <Heading text={t("occurrences")} />
                            <Carousel
                                ref={refOccurrences}
                                width={screenWidth * 0.9}
                                height={110}
                                data={sessionData.occurrences}
                                scrollAnimationDuration={1000}
                                mode="parallax"
                                modeConfig={{
                                    parallaxScrollingScale: 0.9,
                                    parallaxScrollingOffset: 50,
                                }}
                                onProgressChange={progressOccurrences}
                                renderItem={({ item, index }) => (
                                    <View key={index} className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4 flex-row items-center">
                                        {/* Calendar-like date block */}
                                        <View className="bg-white dark:bg-gray-800 p-3 rounded-lg mr-4 justify-center items-center">
                                            <DefaultText text={formatDate(item.occurrence_date)} />
                                        </View>
                                        {/* Occurrence details */}
                                        <View className="flex-1">
                                            <DefaultText text={`${t("occurrenceStatus")}: ${t("occurrenceStatus." + item.status)}`} />
                                            {item.start_datetime && (
                                                <DefaultText text={`${t("occurrence_start_time")}: ${formatTime(item.start_datetime)}`} />
                                            )}
                                            {item.end_datetime && (
                                                <DefaultText text={`${t("occurrence_end_time")}: ${formatTime(item.end_datetime)}`} />
                                            )}
                                        </View>
                                    </View>
                                )}
                            />
                            <Pagination.Basic
                                progress={progressOccurrences}
                                data={sessionData.occurrences}
                                dotStyle={dotStyle}
                                activeDotStyle={activeDotStyle}
                                containerStyle={containerStyle}
                                horizontal
                                onPress={(index) => {
                                    refOccurrences.current?.scrollTo({ count: index - progressOccurrences.value, animated: true });
                                }}
                            />
                        </View>
                    )}

                    {/* Program Carousel */}
                    {loadingProgram ? (
                        <ActivityIndicator size="large" color="#000" />
                    ) : programData && (
                        <View className="mt-8 mb-8">
                            <Heading text={t("eventProgram")} />
                            <Carousel
                                ref={refProgram}
                                width={screenWidth * 0.9}
                                height={200}
                                data={[programData]}
                                scrollAnimationDuration={1000}
                                mode="parallax"
                                modeConfig={{
                                    parallaxScrollingScale: 0.9,
                                    parallaxScrollingOffset: 50,
                                }}
                                onProgressChange={progressProgram}
                                renderItem={({ item, index }) => (
                                    <TouchableOpacity
                                        key={index}
                                        onPress={handleProgramPress}
                                        className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                                    >
                                        <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                                            <DefaultText text={t("programPicturePlaceholder")} />
                                        </View>
                                        <DefaultText text={item.name} />
                                        <DefaultText text={item.description} />
                                        {item.pricing_model === "package" && (
                                            <>
                                                <DefaultText text={t("priceLabel", { price: `€${(item.price / 100).toFixed(2)}` })} />
                                                <DefaultText text={t("capacityLabel", { capacity: item.capacity })} />
                                            </>
                                        )}
                                    </TouchableOpacity>
                                )}
                            />
                            <Pagination.Basic
                                progress={progressProgram}
                                data={[programData]}
                                dotStyle={dotStyle}
                                activeDotStyle={activeDotStyle}
                                containerStyle={containerStyle}
                                horizontal
                                onPress={(index) => {
                                    refProgram.current?.scrollTo({ count: index - progressProgram.value, animated: true });
                                }}
                            />
                        </View>
                    )}
                </View>
                {isLoggedIn && programData && programData.pricing_model === "per_session" && sessionData && (
                    <TouchableOpacity
                        // @ts-ignore
                        onPress={() => { if (!alreadyBooked) router.navigate(`/(tabs)/${route_name}/(view)/BookingPage?club_id=${club_id}&session_id=${session_id}&price=${sessionData.price}`); }}
                        disabled={alreadyBooked}
                        className={`mx-4 mb-4 p-4 rounded-xl items-center justify-center ${alreadyBooked ? 'bg-gray-400' : (colorScheme === 'dark' ? 'bg-white' : 'bg-black')}`}
                    >
                        <Text className={alreadyBooked ? 'text-gray-600' : (colorScheme === 'dark' ? 'text-black' : 'text-white')}>
                            {alreadyBooked ? 'Already booked' : `Book for €${(sessionData.price / 100).toFixed(2)}`}
                        </Text>
                    </TouchableOpacity>
                )}
            </ScrollView>
            <DefaultToast />
        </>
    );
};

export default CoursePageGlobal;