import React from "react";
import { View } from "react-native";
import WeekCalendar from "@/src/components/calendar/WeekCalendar";

const ClubCalendar = () => {
    return (
        <View className="bg-light_primary dark:bg-dark_primary flex-1">
            <WeekCalendar mode="club" />
        </View>
    );
}

export default ClubCalendar;