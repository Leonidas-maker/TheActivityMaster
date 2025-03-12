import React, { useEffect, useState, useCallback } from "react";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import PageNavigator from "@/src/components/pageNavigator/PageNavigator";
import { ScrollView, Pressable, useColorScheme, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useFocusEffect } from "expo-router";
import { getUserClubs } from "@/src/services/user/userService";
import Icon from "react-native-vector-icons/MaterialIcons";
import Heading from "@/src/components/textFields/Heading";
import { useClubContext } from "@/src/provider/ClubProvider";

// Updated Club interface to match the service response
interface Club {
  id: string;
  name: string;
  description: string;
  address: {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
  };
  is_deleted: boolean;
}

const ClubOverview = () => {
  const router = useRouter();
  const navigation = useNavigation();
  const { t } = useTranslation("clubs");
  // State to store clubs
  const [clubs, setClubs] = useState<Club[]>([]);

  // useFocusEffect to fetch clubs when the screen is active
  useFocusEffect(
    useCallback(() => {
      const fetchClubs = async () => {
        try {
          const data: Club[] = await getUserClubs();
          // Filter out clubs that are marked as deleted
          const activeClubs = data.filter((club) => !club.is_deleted);
          setClubs(activeClubs);
        } catch (error) {
          console.error("Failed to fetch clubs:", error);
        }
      };

      fetchClubs();
    }, [])
  );

  // Navigate to club details using the club id and update the global club context.
  const { setClubId } = useClubContext();
  const handleClubDetails = (club_id: string) => {
    setClubId(club_id);
    router.navigate(`/(tabs)/clubs/ClubManagement?club_id=${club_id}`);
  };

  // ====================================================== //
  // ================= CreateClubNavigator ================ //
  // ====================================================== //
  const handleCreateClub = () => {
    router.push("/(tabs)/clubs/ClubCreate");
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

  const [isLight, setIsLight] = useState(false);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setIsLight(colorScheme === "light");
  }, [colorScheme]);
  const iconColor = isLight ? "#000000" : "#FFFFFF";

  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Pressable onPress={handleCreateClub}>
          <Icon
            name="add"
            size={30}
            color={iconColor}
            style={{ marginLeft: "auto", marginRight: 15 }}
          />
        </Pressable>
      ),
    });
  }, [navigation, iconColor]);

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
      {clubs.length === 0 && (
        <View className="py-4">
          <Heading text={t("no_clubs_available")} />
        </View>
      )}
      {/* <PageNavigator
        title={createClubTitle}
        texts={createClubTexts}
        iconNames={createClubIcons}
        onPressFunctions={onPressCreateClubFunctions}
      /> */}
    </ScrollView>
  );
};

export default ClubOverview;
