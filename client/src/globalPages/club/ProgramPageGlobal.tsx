import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme, Text } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import Subheading from "@/src/components/textFields/Subheading";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

// Import the services
import { getProgram } from "@/src/services/club/programService";
import { getMembership } from "@/src/services/club/membershipService";
import { getUserSessions } from "@/src/services/user/userService";

import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

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

interface Session {
  session_type: string; // e.g., 'course' or 'event'
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

const ProgramPageGlobal = ({ club_id, program_id, route_name }: { club_id: string | string[], program_id: string | string[], route_name: string | string[] }) => {
  const router = useRouter();
  const { t } = useTranslation("clubs");

  const [programData, setProgramData] = useState<ProgramResponse | null>(null);
  const [membershipDetails, setMembershipDetails] = useState<MembershipResponse[]>([]);
  const [loadingProgram, setLoadingProgram] = useState<boolean>(true);
  const [loadingMemberships, setLoadingMemberships] = useState<boolean>(false);
  const [userSessions, setUserSessions] = useState<any[]>([]);
  const [isLight, setIsLight] = useState(false);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setIsLight(colorScheme === "light");
  }, [colorScheme]);

  // Shared values and refs for carousels
  const progressMemberships = useSharedValue(0);
  const progressSessions = useSharedValue(0);
  const refMemberships = useRef<ICarouselInstance>(null);
  const refSessions = useRef<ICarouselInstance>(null);

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

  const screenWidth = Dimensions.get("window").width;

  // Utility function to truncate text
  const truncate = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  useEffect(() => {
    getUserSessions()
      .then((data) => setUserSessions(data))
      .catch((error) => {
        console.error("Error fetching user sessions", error);
      });
  }, []);

  const alreadyBooked = programData ? userSessions.some((p: any) => p.id === programData.id) : false;

  useEffect(() => {
    // Fetch program details
    getProgram(club_id, program_id)
      .then((data: ProgramResponse) => {
        setProgramData(data);
        // If membership is required and there are membership_ids, fetch each membership
        if (data.membership_required && data.membership_ids && data.membership_ids.length > 0) {
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

  // Dummy navigation handlers for sessions
  const handleSessionPress = (session: Session) => {
    if (session.session_type === "course") {
      // @ts-ignore
      router.navigate(`/(tabs)/${route_name}/(view)/CoursePage?club_id=${club_id}&program_id=${programData?.id}&session_id=${session.id}&pricing_model=${programData?.pricing_model}`);
    } else if (session.session_type === "event") {
      // @ts-ignore
      router.navigate(`/(tabs)/${route_name}/(view)/EventPage?club_id=${club_id}&program_id=${programData?.id}&session_id=${session.id}&pricing_model=${programData?.pricing_model}`);
    } else {
      // Fallback navigation
      // @ts-ignore
      router.back();
    }
  };

  // Define a function to render session details based on session type and pricing model
  const renderSessionDetails = (session: Session) => {
    if (!programData) return null;
    const details = [];

    // Helper to format a date string to DD.MM.YYYY
    const formatDate = (dateString: string) => {
      const date = new Date(dateString);
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}.${month}.${year}`;
    };

    // Helper to format a full datetime string to HH:MM (24-hour format)
    const formatTime = (dateString: string) => {
      const date = new Date(dateString);
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;
    };

    // Helper to format course time strings (which might be time-only) by prefixing an arbitrary date
    const formatCourseTime = (timeString: string) => {
      return formatTime(`1970-01-01T${timeString}`);
    };

    // If pricing model is per_session, always display price and capacity
    if (programData.pricing_model === "per_session") {
      details.push(
        <DefaultText key="price" text={t("priceLabel", { price: `€${(session.price / 100).toFixed(2)}` })} />,
        <DefaultText key="capacity" text={t("capacityLabel", { capacity: session.capacity })} />
      );
    }

    // Additional details for event sessions
    if (session.session_type === "event") {
      details.push(
        <DefaultText key="date" text={`${t("event_date")}: ${formatDate(session.start_datetime)}`} />,
        <DefaultText key="start_time" text={`${t("start_time")}: ${formatTime(session.start_datetime)}`} />,
        <DefaultText key="end_time" text={`${t("end_time")}: ${formatTime(session.end_datetime)}`} />
      );
    }

    // Additional details for course sessions
    if (session.session_type === "course") {
      // Translate weekday if available
      details.push(
        <DefaultText key="day_of_week" text={`${t("day_of_week")}: ${session.day_of_week ? t("weekday." + session.day_of_week) : ''}`} />
      );
      // If end_date is defined, display date range; otherwise, display only the start date with a different label
      if (session.end_date && session.start_date) {
        details.push(
          <DefaultText key="dateRange" text={`${t("dateRange")}: ${formatDate(session.start_date)} - ${formatDate(session.end_date)}`} />
        );
      } else if (session.start_date) {
        details.push(
          <DefaultText key="date" text={`${t("start_dateLabel")}: ${formatDate(session.start_date)}`} />
        );
      }
      // Display course times formatted to HH:MM in 24-hour format
      if (session.start_time) {
        details.push(
          <DefaultText key="start_time" text={`${t("start_time")}: ${formatCourseTime(session.start_time)}`} />
        );
      }
      if (session.end_time) {
        details.push(
          <DefaultText key="end_time" text={`${t("end_time")}: ${formatCourseTime(session.end_time)}`} />
        );
      }
    }

    return details;
  };

  // Function to render address if available
  const renderAddress = (address: Session['address']) => {
    if (!address) return null;
    return (
      <DefaultText text={`${address.street}, ${address.city}, ${address.state}, ${address.postal_code}, ${address.country}`} />
    );
  };

  return (
    <>
      <ScrollView className="bg-light_primary dark:bg-dark_primary">
        <View className="p-4">
          {/* Program Picture Placeholder */}
          <View className="w-full h-52 bg-gray-300 dark:bg-gray-700 justify-center items-center mb-4 rounded-xl">
            <DefaultText text={t("programPicturePlaceholder")} />
          </View>

          {/* Program Details */}
          {loadingProgram ? (
            <ActivityIndicator size="large" color="#000" />
          ) : programData ? (
            <View>
              <Heading text={programData.name} />
              <Subheading text={t("program_details")} />
              <View className="py-2">
                <DefaultText text={programData.description} />
              </View>
              <View className="py-2">
                {programData.pricing_model === "package" ? (
                  <>
                    <DefaultText text={t("priceLabel", { price: `€${(programData.price / 100).toFixed(2)}` })} />
                    <DefaultText text={t("capacityLabel", { capacity: programData.capacity })} />
                  </>
                ) : (
                  <DefaultText text={t("pricingPerSession")} />
                )}
              </View>
              {/* Categories */}
              {programData.categories.length > 0 && (
                <View className="py-2">
                  <Subheading text={t("categoriesLabel")} />
                  {programData.categories.map((category, index) => (
                    <DefaultText key={index} text={category.name} />
                  ))}
                </View>
              )}
              {/* Membership Requirement */}
              {programData.membership_required && (
                <View className="py-2">
                  <Subheading text={t("membershipRequired")} />
                  {loadingMemberships ? (
                    <ActivityIndicator size="large" color="#000" />
                  ) : membershipDetails.length === 0 ? (
                    <Subheading text={t("noMembershipsAvailable")} />
                  ) : (
                    <>
                      <Carousel
                        ref={refMemberships}
                        width={screenWidth * 0.9}
                        height={200}
                        data={membershipDetails}
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
                            // @ts-ignore
                            onPress={() => router.navigate(`/(tabs)/${route_name}/(view)/MembershipPage?club_id=${club_id}&membership_id=${item.id}`)}
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
                      <Pagination.Basic
                        progress={progressMemberships}
                        data={membershipDetails}
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
              )}

              {/* Sessions Carousel */}
              <View className="mt-8 mb-8">
                <Heading text={t("sessionsTitle")} />
                {programData.sessions.length === 0 ? (
                  <Subheading text={t("noSessionsAvailable")} />
                ) : (
                  <>
                    <Carousel
                      ref={refSessions}
                      width={screenWidth * 0.9}
                      height={150}
                      data={programData.sessions}
                      scrollAnimationDuration={1000}
                      mode="parallax"
                      modeConfig={{
                        parallaxScrollingScale: 0.9,
                        parallaxScrollingOffset: 50,
                      }}
                      onProgressChange={progressSessions}
                      renderItem={({ item, index }) => {
                        const bgColor = isLight
                          ? (item.session_type === "course" ? "#FF4000" : item.session_type === "event" ? "#50B2C0" : "#D3D3D3")
                          : (item.session_type === "course" ? "#A32900" : item.session_type === "event" ? "#2B6E78" : "#696969");
                        return (
                          <TouchableOpacity
                            key={index}
                            onPress={() => handleSessionPress(item)}
                            style={{ backgroundColor: bgColor }}
                            className="mx-2 rounded-xl p-4"
                          >
                            <DefaultText text={`${t("sessionType")}: ${t("session_type." + item.session_type)}`} />
                            {renderSessionDetails(item)}
                            {item.address && renderAddress(item.address)}
                          </TouchableOpacity>
                        );
                      }}
                    />
                    <Pagination.Basic
                      progress={progressSessions}
                      data={programData.sessions}
                      dotStyle={dotStyle}
                      activeDotStyle={activeDotStyle}
                      containerStyle={containerStyle}
                      horizontal
                      onPress={(index) => {
                        refSessions.current?.scrollTo({ count: index - progressSessions.value, animated: true });
                      }}
                    />
                  </>
                )}
              </View>
            </View>
          ) : null}
        </View>
        {programData && programData.pricing_model === "package" && (
          <TouchableOpacity
           // @ts-ignore
           onPress={() => { if (!alreadyBooked) router.navigate(`/(tabs)/${route_name}/(view)/BookingPage?club_id=${club_id}&program_id=${programData.id}&price=${programData.price}&name=${programData.name}`); 
           }}
            disabled={alreadyBooked}
            className={`mx-4 my-4 p-4 rounded-xl items-center justify-center ${alreadyBooked ? 'bg-gray-400' : (colorScheme === 'dark' ? 'bg-white' : 'bg-black')
              }`}
          >
            <Text className={alreadyBooked ? 'text-gray-600' : (colorScheme === 'dark' ? 'text-black' : 'text-white')}>
              {alreadyBooked ? 'Already booked' : `Book for €${(programData.price / 100).toFixed(2)}`}
            </Text>
          </TouchableOpacity>
        )}
      </ScrollView>
      <DefaultToast />
    </>
  );
};

export default ProgramPageGlobal;