import React, { useEffect, useState, useRef } from "react";
import { ScrollView, View, ActivityIndicator, Dimensions, TouchableOpacity, useColorScheme } from "react-native";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import { useSharedValue } from "react-native-reanimated";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getClub } from "@/src/services/club/clubService";
import { getMemberships } from "@/src/services/club/membershipService";
import { getPrograms } from "@/src/services/club/programService";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Subheading from "@/src/components/textFields/Subheading";

const SessionPageGlobal = ({ club_id, program_id, session_id, route_name }: { club_id: string | string[], program_id: string | string[], session_id: string | string[], route_name: string | string[] }) => {
    const router = useRouter();
    const { t } = useTranslation("clubs");

    return (
        <View className="h-screen bg-light_primary dark:bg-dark_primary">
            <DefaultText text="Session Page" />
        </View>
    );
};

export default SessionPageGlobal;