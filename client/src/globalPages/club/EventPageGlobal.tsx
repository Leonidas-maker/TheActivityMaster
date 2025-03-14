import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme, Text } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import Subheading from "@/src/components/textFields/Subheading";
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

interface Session {
  session_type: string;
  capacity: number;
  price: number;
  start_datetime: string;
  end_datetime: string;
  day_of_week?: string;
  start_time?: string;
  end_time?: string;
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
  occurrences?: any[];
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


const EventPageGlobal = ({ club_id, program_id, session_id, pricing_model, route_name }:
  { club_id: string | string[], program_id: string | string[], session_id: string | string[], pricing_model: string | string[], route_name: string | string[] }) => {
  const router = useRouter();
  const { t } = useTranslation("clubs");
  const colorScheme = useColorScheme();
  const screenWidth = Dimensions.get("window").width;

  const { authState } = useAuth();
  const { isLoggedIn } = authState;

  // State for session details and program details
  const [sessionData, setSessionData] = useState<Session | null>(null);
  const [programData, setProgramData] = useState<ProgramResponse | null>(null);
  const [loadingSession, setLoadingSession] = useState<boolean>(true);
  const [loadingProgram, setLoadingProgram] = useState<boolean>(true);
  const [userSessions, setUserSessions] = useState<any[]>([]);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);
  const [membershipDetails, setMembershipDetails] = useState<MembershipResponse[]>([]);
  const [loadingMemberships, setLoadingMemberships] = useState<boolean>(false);

  // Shared value and ref for program carousel
  const progressProgram = useSharedValue(0);
  const refProgram = useRef<ICarouselInstance>(null);

  // Utility functions to format date and time
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  // Helper function to render address
  const renderAddress = (address: Session['address']) => {
    if (!address) return null;
    return (
      <DefaultText text={`${address.street}, ${address.city}, ${address.state}, ${address.postal_code}, ${address.country}`} />
    );
  };

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
            text1: t("eventNotFound"),
            text2: t("eventNotFoundDesc"),
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
      .then((data) => setUserSessions(data))
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

  const alreadyBooked = sessionData ? userSessions.some((course: any) => course.sessions.some((s: any) => s.id === sessionData.id)) : false;

  // Handler for navigating to program details when clicking on carousel item
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
              <Heading text={t("eventDetails")} />
              <View className="py-2">
                <DefaultText text={`${t("sessionType")}: ${t("session_type." + sessionData.session_type)}`} />
                {programData && programData.pricing_model === "per_session" && (
                  <>
                    <DefaultText text={t("priceLabel", { price: `€${(sessionData.price / 100).toFixed(2)}` })} />
                    <DefaultText text={t("capacityLabel", { capacity: sessionData.capacity })} />
                  </>
                )}
                <DefaultText text={`${t("event_date")}: ${formatDate(sessionData.start_datetime)}`} />
                <DefaultText text={`${t("start_time")}: ${formatTime(sessionData.start_datetime)}`} />
                <DefaultText text={`${t("end_time")}: ${formatTime(sessionData.end_datetime)}`} />
                {sessionData.address && renderAddress(sessionData.address)}
              </View>
            </View>
          ) : null}

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
                    {/* Program Picture Placeholder */}
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
            className={`mx-4 my-4 p-4 rounded-xl items-center justify-center ${alreadyBooked ? 'bg-gray-400' : (colorScheme === 'dark' ? 'bg-white' : 'bg-black')}`}
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

export default EventPageGlobal;