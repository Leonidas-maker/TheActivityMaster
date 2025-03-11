import React, { useState, useEffect } from "react";
import { ScrollView } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import { deleteSession } from "@/src/services/club/programSessionService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Icon from "react-native-vector-icons/MaterialIcons";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";

interface Occurrence {
    id: string;
    session_id: string;
    status: string;
    occurrence_date: string;
    start_datetime?: string;
    end_datetime?: string;
    note?: string;
}

// Function to convert a date string from "YYYY-MM-DD" to "DD.MM.YYYY"
const formatDate = (dateStr: string): string => {
    const parts = dateStr.split("-");
    if (parts.length === 3) {
        return `${parts[2]}.${parts[1]}.${parts[0]}`;
    }
    return dateStr;
};

// Function to format a time string to "HH:MM"
// It checks if the time string includes a "T" (ISO format) and uses Date if so
const formatTime = (timeStr: string): string => {
    if (timeStr.includes("T")) {
        const date = new Date(timeStr);
        const hh = date.getHours().toString().padStart(2, "0");
        const mm = date.getMinutes().toString().padStart(2, "0");
        return `${hh}:${mm}`;
    }
    // Otherwise, assume the format is "HH:MM:SS" and take the first 5 characters
    return timeStr.slice(0, 5);
};

const ManageSession = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const {
        club_id,
        program_id,
        session_id,
        pricing_model,
        day_of_week,
        start_time,
        end_time,
        start_date,
        end_date,
        occurrences,
        capacity_event,
        price_event
    } = useLocalSearchParams();

    // State to hold the parsed occurrences array
    const [occurrenceList, setOccurrenceList] = useState<Occurrence[]>([]);

    useEffect(() => {
        console.log(
            club_id,
            program_id,
            session_id,
            pricing_model,
            day_of_week,
            start_time,
            end_time,
            start_date,
            end_date,
            occurrences,
            capacity_event,
            price_event
        );
        let occurrencesStr = "";
        if (Array.isArray(occurrences)) {
            occurrencesStr = occurrences[0];
        } else if (typeof occurrences === "string") {
            occurrencesStr = occurrences;
        }
        const parsedOccurrences = occurrencesStr
            ? JSON.parse(decodeURIComponent(occurrencesStr))
            : [];
        console.log(parsedOccurrences);
        setOccurrenceList(parsedOccurrences);
    }, [
        club_id,
        program_id,
        session_id,
        pricing_model,
        day_of_week,
        start_time,
        end_time,
        start_date,
        end_date,
        occurrences,
        capacity_event,
        price_event
    ]);

    const handleCourseUpdatePress = () => {
        router.navigate(
            `/(tabs)/clubs/(session)/ManageCourse?club_id=${club_id}&program_id=${program_id}&session_id=${session_id}&pricing_model=${pricing_model}&day_of_week=${day_of_week}&start_time=${start_time}&end_time=${end_time}&start_date=${start_date}&end_date=${end_date}&occurrences=${occurrences}&capacity_event=${capacity_event}&price_event=${price_event}`
        );
    };

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <PageNavigator
                title={t("manageCourse_navigationTitle")}
                texts={[t("update_course")]}
                iconNames={["edit"]}
                onPressFunctions={[handleCourseUpdatePress]}
            />
            {/* Occurrences Navigator */}
            {occurrenceList.length > 0 && (
                <PageNavigator
                    title={t("occurrences_navigationTitle") || "Occurrences"}
                    texts={occurrenceList.map((occurrence: Occurrence) => {
                        const formattedDate = formatDate(occurrence.occurrence_date);
                        const formattedTime = occurrence.start_datetime
                            ? formatTime(occurrence.start_datetime)
                            : "";
                        return formattedTime
                            ? `${t("occurrenceOn")} ${formattedDate} ${formattedTime}`
                            : `${t("occurrenceOn")} ${formattedDate}`;
                    })}
                    iconNames={occurrenceList.map(() => "calendar-today")}
                    onPressFunctions={occurrenceList.map((occurrence: Occurrence) => () => {
                        router.navigate(
                            `/(tabs)/clubs/(session)/ManageOccurrence?club_id=${club_id}&program_id=${program_id}&session_id=${session_id}&occurrence_id=${occurrence.id}`
                        );
                    })}
                />
            )}
        </ScrollView>
    );
};

export default ManageSession;
