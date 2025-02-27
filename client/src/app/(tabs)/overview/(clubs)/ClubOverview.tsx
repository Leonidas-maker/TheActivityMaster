import React, { useEffect, useState } from "react";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { ScrollView } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useFocusEffect } from "expo-router";
import { getUserClubs } from "@/src/services/user/userService";

interface Club {
    id: string;
    name: string;
  }

const ClubOverview = () => {
    const router = useRouter();
    const { t } = useTranslation("clubs");
    // State to store only club names
    const [clubs, setClubs] = useState<Club[]>([]);

    useEffect(() => {
        const fetchClubs = async () => {
            try {
                const data: Club[] = await getUserClubs();
                setClubs(data);
            } catch (error) {
                console.error("Failed to fetch clubs:", error);
            }
        };

        fetchClubs();
    }, []);

    // Navigate to club details using the club name
    const handleClubDetails = (club_id: string) => {
        router.navigate(`/(tabs)/overview/(clubs)/ClubManagement?club_id=${club_id}`);
    };

    // ====================================================== //
    // ================= CreateClubNavigator ================ //
    // ====================================================== //
    const handleCreateClub = () => {
        router.push("/(tabs)/overview/(clubs)/ClubCreate");
    };

    const createClubTitle = t("createClub_navigator_title");

    const onPressCreateClubFunctions = [handleCreateClub];

    const createClubTexts = [t("createClub_btn")];

    const createClubIcons = ["add"];

    // Map the clubs to arrays expected by PageNavigator
    const texts = clubs.map((club) => club.name);
    const onPressFunctions = clubs.map((club) => () => handleClubDetails(club.id));
    // Using a default icon name for each club; adjust as needed
    const iconNames = clubs.map(() => "group");

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            {clubs.length > 0 && (
                <PageNavigator
                    title={t("myClubs_navigator_title")}
                    texts={texts}
                    onPressFunctions={onPressFunctions}
                    iconNames={iconNames}
                />
            )}
            <PageNavigator
                title={createClubTitle}
                texts={createClubTexts}
                iconNames={createClubIcons}
                onPressFunctions={onPressCreateClubFunctions}
            />
        </ScrollView>
    );
};

export default ClubOverview;
