import React, { useEffect } from "react";
import { View } from "react-native";
import WeekCalendar from "@/src/components/calendar/WeekCalendar";
import { useTranslation } from "react-i18next";

export default function Tab() {
    const { t } = useTranslation("calendar");

    return (
        <View className="bg-light_primary dark:bg-dark_primary flex-1">
            <WeekCalendar />
        </View>
    );
};