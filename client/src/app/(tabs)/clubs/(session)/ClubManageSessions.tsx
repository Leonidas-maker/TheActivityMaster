import React, { useState, useEffect, useCallback } from "react";
import {
    ScrollView,
    View,
    useColorScheme,
    Pressable
} from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import {
    useRouter,
    useNavigation,
    useLocalSearchParams,
    useFocusEffect
} from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { getSessions } from "@/src/services/club/programSessionService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

// Define a Session interface based on the expected data structure
interface Session {
    session_type: "event" | "course";
    capacity: number;
    price: number;
    start_datetime?: string;
    end_datetime?: string;
    id: string;
    program_id: string;
    day_of_week?: string;
    start_time?: string;
    end_time?: string;
    start_date?: string;
    occurrences?: any[];
}

// Helper function to format a date string (YYYY-MM-DD or full ISO) to DD.MM.YYYY
const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
};

const ClubManageSessions = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, program_id, pricing_model } = useLocalSearchParams();

    // State to hold sessions data with proper typing
    const [sessions, setSessions] = useState<Session[]>([]);

    // State to track theme (light or dark)
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // Function to handle the "Add" button press
    const handleAddPress = () => {
        router.push(`/(tabs)/clubs/(session)/AddSession?club_id=${club_id}&program_id=${program_id}&pricing_model=${pricing_model}`);
    };

    // Fetch sessions when the screen is focused
    useFocusEffect(
        useCallback(() => {
            const fetchSessions = async () => {
                try {
                    const data = await getSessions(club_id, program_id);
                    setSessions(data);
                } catch (error) {
                    Toast.show({
                        type: "error",
                        text1: t("sessionFetchError"),
                        text2: t("sessionFetchErrorDescription")
                    });
                }
            };
            fetchSessions();
        }, [club_id, program_id])
    );

    // Set the header "add" icon in the navigation options
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
            )
        });
    }, [navigation, iconColor]);

    // Split sessions into events and courses
    const eventSessions = sessions.filter(session => session.session_type === "event");
    const courseSessions = sessions.filter(session => session.session_type === "course");

    // Prepare texts and onPress functions for the events PageNavigator
    const eventTexts = eventSessions.map(event => {
        // Format event start date/time if available
        const startDate = new Date(event.start_datetime as string);
        return `${t("eventOn")} ${formatDate(startDate.toISOString())} ${startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}`;
    });
    const eventOnPressFunctions = eventSessions.map(event => () => {
        router.push(`/(tabs)/clubs/(session)/ManageSession?club_id=${club_id}&program_id=${program_id}&session_id=${event.id}`);
    });
    const eventIconNames = eventSessions.map(() => "event");

    // Prepare texts and onPress functions for the courses PageNavigator
    const courseTexts = courseSessions.map(course => {
        // Format the start_date and trim the start_time to HH:MM
        const formattedDate = course.start_date ? formatDate(course.start_date) : "";
        const formattedTime = course.start_time ? course.start_time.substring(0, 5) : "";
        // For courses, display start date, day of week and start time if available
        const translatedDay = course.day_of_week ? t(course.day_of_week.toLowerCase()) : "";
        return `${t("courseOn")} ${formattedDate} (${translatedDay}) ${formattedTime}`;
    });
    const courseOnPressFunctions = courseSessions.map(course => () => {
        router.push(`/(tabs)/clubs/(session)/ManageSession?club_id=${club_id}&program_id=${program_id}&session_id=${course.id}`);
    });
    const courseIconNames = courseSessions.map(() => "school");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            {sessions.length > 0 ? (
                <>
                    {eventSessions.length > 0 && (
                        <PageNavigator
                            title={t("events_navigator_title")}
                            texts={eventTexts}
                            onPressFunctions={eventOnPressFunctions}
                            iconNames={eventIconNames}
                        />
                    )}
                    {courseSessions.length > 0 && (
                        <PageNavigator
                            title={t("courses_navigator_title")}
                            texts={courseTexts}
                            onPressFunctions={courseOnPressFunctions}
                            iconNames={courseIconNames}
                        />
                    )}
                </>
            ) : (
                <View className="py-4">
                    <Heading text={t("noSessions")} />
                </View>
            )}
            <DefaultToast />
        </ScrollView>
    );
};

export default ClubManageSessions;
