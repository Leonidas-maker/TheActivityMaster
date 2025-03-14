// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { useState, useCallback, useEffect, useRef } from "react";
import {
    View,
    LayoutAnimation,
    UIManager,
    Platform,
    Alert,
} from "react-native";
import "nativewind";
import { addWeeks, subWeeks } from "date-fns";
import { FlingGestureHandler, Directions } from "react-native-gesture-handler";
import { useFocusEffect } from "@react-navigation/native";
import * as Progress from "react-native-progress";
import { useNavigation } from "@react-navigation/native";
import { getUserSessions } from "@/src/services/user/userService";
import { getProgramsDetails } from "@/src/services/club/programService";
import { useClubContext } from "@/src/provider/ClubProvider";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import Days from "./Days";
import WeekSelector from "../selector/WeekSelector";

// ~~~~~~~~~~ Interfaces imports ~~~~~~~~~ //
import {
    CalendarProps,
    EventTimeProps,
} from "../../interfaces/calendarInterfaces";

// Important for LayoutAnimation on Android according to the docs
//! Disabled because it causes a crash on Android
// if (Platform.OS === "android") {
//   if (UIManager.setLayoutAnimationEnabledExperimental) {
//     UIManager.setLayoutAnimationEnabledExperimental(true);
//   }
// }

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const WeekCalendar: React.FC<{ mode: string }> = ({ mode }) => {
    // ====================================================== //
    // ======================= States ======================= //
    // ====================================================== //
    // Gets the current date
    const [currentDate, setCurrentDate] = useState(new Date());
    const [events, setEvents] = useState<EventTimeProps[]>([]);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const navigation = useNavigation<any>();
    const { clubId } = useClubContext();

    const FETCH_SESSIONS_INTERVAL = 60000;

    const lastFetchTimeRef = useRef<number | null>(null);

    useFocusEffect(
        useCallback(() => {
            const now = Date.now();
            // Only fetch session again if it's been more than FETCH_SESSIONS_INTERVAL since the last fetch
            if (!lastFetchTimeRef.current || (now - lastFetchTimeRef.current) > FETCH_SESSIONS_INTERVAL) {
                const fetchUserSessions = async () => {
                    try {
                        let sessionsResponse: any;
                        if (mode === "user") {
                            sessionsResponse = await getUserSessions();
                        } else if (mode === "club") {
                            if (!clubId) {
                                throw new Error("Club ID is null");
                            }
                            sessionsResponse = await getProgramsDetails(clubId, 1, 50);
                        }
                        let newEvents: EventTimeProps[] = [];

                        // Iterate over each session group in the response
                        sessionsResponse.forEach((sessionGroup: any) => {
                            const name = sessionGroup.name;
                            const description = sessionGroup.description;

                            // Iterate over each session inside the group
                            sessionGroup.sessions.forEach((session: any) => {
                                // Check session type
                                if (session.session_type === 'event') {
                                    // For events, use start_datetime and end_datetime
                                    const eventItem: any = {
                                        name,
                                        description,
                                        start: new Date(session.start_datetime),
                                        end: new Date(session.end_datetime),
                                        session_type: session.session_type,
                                    };
                                    // If address exists, add it
                                    if (session.address) {
                                        eventItem.address = session.address;
                                    }
                                    newEvents.push(eventItem);
                                } else if (session.session_type === 'course') {
                                    // For courses, use start_date and end_date as event times
                                    // const courseEvent: any = {
                                    //    name,
                                    //   description,
                                    //  start: session.start_date,
                                    //  end: session.end_date,
                                    //};
                                    // newEvents.push(courseEvent);

                                    // Iterate over occurrences to create separate events
                                    if (session.occurrences && Array.isArray(session.occurrences)) {
                                        session.occurrences.forEach((occ: any) => {
                                            const occurrenceEvent: any = {
                                                name,
                                                description,
                                                status: occ.status,
                                                session_type: session.session_type,
                                            };

                                            // Include note if available
                                            if (occ.note) {
                                                occurrenceEvent.note = occ.note;
                                            }

                                            // Determine start and end times for the occurrence event
                                            if (occ.start_datetime && occ.end_datetime) {
                                                // Use occurrence's start and end datetimes if available
                                                occurrenceEvent.start = new Date(occ.start_datetime);
                                                occurrenceEvent.end = new Date(occ.end_datetime);
                                            } else {
                                                // Fallback: use session's start_time and end_time combined with occurrence_date
                                                // Construct Date objects by combining occurrence_date with the session times
                                                const occurrenceDate = occ.occurrence_date;
                                                occurrenceEvent.start = new Date(`${occurrenceDate}T${session.start_time}`);
                                                occurrenceEvent.end = new Date(`${occurrenceDate}T${session.end_time}`);
                                            }
                                            newEvents.push(occurrenceEvent);
                                        });
                                    }
                                }
                            });
                        });
                        setEvents(newEvents);
                    } catch (error) {
                        console.error('Error fetching user sessions', error);
                    }
                };
                fetchUserSessions();
                lastFetchTimeRef.current = now;
            }
        }, [])
    );

    // ====================================================== //
    // ===================== Animations ===================== //
    // ====================================================== //
    // Defines the animation for the transition between weeks (animation: easeInEaseOut)
    //! Disabled animation on Android because it causes a crash
    const animateTransition = () => {
        if (Platform.OS === "android") {
        } else {
            LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        }
    };

    // useFocusEffect(
    //     useCallback(() => {
    //         const loadEvents = async () => {
    //             setLoading(true);
    //             setProgress(0.3);
    //             await loadEventsFromStorage(setEvents);
    //             setProgress(0.6);
    //             // Function to try fetching the new uuid
    //             // If it does not work, user has to select a new university
    //             try {
    //                 const fetchedEvents = await fetchEvents();

    //                 if (fetchedEvents.length > 0) {
    //                     setEvents(fetchedEvents);
    //                 } else {
    //                     setProgress(1);
    //                     setLoading(false);
    //                     return;
    //                 }
    //             } catch (error) {
    //                 if (axios.isAxiosError(error)) {
    //                     if (
    //                         error.response?.status !== 404 &&
    //                         error.response?.status !== 422
    //                     ) {
    //                         throw new Error("Error fetching events");
    //                     }
    //                     try {
    //                         const fetchedCalendars = await fetchCalendars();
    //                         const currentCalendar =
    //                             await AsyncStorage.getItem("selectedUniversity");

    //                         if (fetchedCalendars.length > 0 && currentCalendar) {
    //                             const calendarObject = JSON.parse(currentCalendar);
    //                             const selectedUniversityName = calendarObject.name;
    //                             const matchingCalendar = fetchedCalendars.find(
    //                                 (calendar) =>
    //                                     calendar.university_name === selectedUniversityName,
    //                             );

    //                             if (matchingCalendar) {
    //                                 const newSelectedUniversity = {
    //                                     name: selectedUniversityName,
    //                                     uuid: matchingCalendar.university_uuid,
    //                                 };
    //                                 await AsyncStorage.setItem(
    //                                     "selectedUniversity",
    //                                     JSON.stringify(newSelectedUniversity),
    //                                 );

    //                                 const fetchedEvents = await fetchEvents(true);

    //                                 if (fetchedEvents.length > 0) {
    //                                     setEvents(fetchedEvents);
    //                                 } else {
    //                                     throw new Error("Error fetching events");
    //                                 }
    //                             } else {
    //                                 throw new Error("No calendars found.");
    //                             }
    //                         } else {
    //                             throw new Error("No selected university found.");
    //                         }
    //                     } catch (error) {
    //                         console.error("Error setting uuid new", error);

    //                         await AsyncStorage.removeItem("selectedUniversity");
    //                         await AsyncStorage.removeItem("selectedCourse");
    //                         await AsyncStorage.removeItem("events");

    //                         Alert.alert(
    //                             "Calendar nicht verfügbar",
    //                             "Der gewählte Kalender ist nicht verfügbar. Bitte wählen Sie einen neuen Kalender aus.",
    //                             [
    //                                 {
    //                                     text: "Zurück",
    //                                     style: "cancel",
    //                                 },
    //                                 {
    //                                     text: "Zur Auswahl",
    //                                     onPress: () => {
    //                                         navigation.navigate("MiscStack", { screen: "Settings" });
    //                                     },
    //                                     style: "default",
    //                                 },
    //                             ],
    //                             { cancelable: false },
    //                         );
    //                     }
    //                 } else {
    //                     console.error("Error fetching events", error);
    //                 }
    //             }
    //             setProgress(1);
    //             setLoading(false);
    //         };

    //         const checkSelections = async () => {
    //             let missingUniversity = false;
    //             let missingCourse = false;

    //             await getSelectedUniversity(
    //                 () => { },
    //                 () => { },
    //                 (missing) => {
    //                     missingUniversity = missing;
    //                 },
    //             );
    //             await getSelectedCourse(
    //                 () => { },
    //                 () => { },
    //                 (missing) => {
    //                     missingCourse = missing;
    //                 },
    //             );

    //             if (missingUniversity || missingCourse) {
    //                 Alert.alert(
    //                     "Auswahl erforderlich",
    //                     "Bitte wählen Sie eine Universität und einen Kurs aus.",
    //                     [
    //                         {
    //                             text: "Zurück",
    //                             style: "cancel",
    //                         },
    //                         {
    //                             text: "Zur Auswahl",
    //                             onPress: () => {
    //                                 navigation.navigate("MiscStack", { screen: "Settings" });
    //                             },
    //                             style: "default",
    //                         },
    //                     ],
    //                     { cancelable: false },
    //                 );
    //             }
    //         };

    //         loadEvents();
    //         checkSelections();
    //     }, [navigation]),
    // );

    // ====================================================== //
    // =================== Press handlers =================== //
    // ====================================================== //
    // Handles the back press by subtracting a week from the current displayed date
    const handleBackPress = () => {
        animateTransition();
        setCurrentDate((current) => subWeeks(current, 1));
    };

    // Handles the forward press by adding a week to the current displayed date
    const handleForwardPress = () => {
        animateTransition();
        setCurrentDate((current) => addWeeks(current, 1));
    };

    // Handles the today press by setting the current displayed date to the current date
    const handleTodayPress = () => {
        animateTransition();
        setCurrentDate(new Date());
    };

    //TODO Add scrolling in web version
    // ====================================================== //
    // ================== Return component ================== //
    // ====================================================== //
    // nativeEvent.state === 5 is the end of the gesture
    return (
        <FlingGestureHandler
            direction={Directions.LEFT}
            onHandlerStateChange={({ nativeEvent }) => {
                if (nativeEvent.state === 5) handleForwardPress();
            }}
        >
            <FlingGestureHandler
                direction={Directions.RIGHT}
                onHandlerStateChange={({ nativeEvent }) => {
                    if (nativeEvent.state === 5) handleBackPress();
                }}
            >
                <View className="h-full flex-1">
                    <WeekSelector
                        mode="calendar"
                        onBackPress={handleBackPress}
                        onForwardPress={handleForwardPress}
                        onTodayPress={handleTodayPress}
                    />
                    {loading && <Progress.Bar progress={progress} width={null} />}
                    <Days currentDate={currentDate} events={events} />
                </View>
            </FlingGestureHandler>
        </FlingGestureHandler>
    );
};

export default WeekCalendar;
