import React, { useEffect } from "react";
import { View } from "react-native";
import WeekCalendar from "@/src/components/calendar/WeekCalendar";
import { useTranslation } from "react-i18next";
import { getUserData } from "@/src/services/user/userService";

export default function Tab() {
    const { t } = useTranslation("calendar");
    const userDate = async () => {
        const response = getUserData();
        console.log(response);
    };

    useEffect(() => {
        userDate();
    }, []);

    return (
        <View className="bg-light_primary dark:bg-dark_primary flex-1">
            <WeekCalendar />
        </View>

    );
};