import React, { useState, useEffect } from "react";
import { ScrollView, View, useColorScheme, Alert, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import { createProgram } from "@/src/services/club/programService";
import { getProgramCategories } from "@/src/services/club/programService";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import { getClubPermissions } from "@/src/services/club/roleService";

const AddRole = () => {
  const router = useRouter();
  const navigation = useNavigation();
  const { t } = useTranslation("clubs");
  const { club_id } = useLocalSearchParams();

  // State to track the color scheme
  const [isLight, setIsLight] = useState(false);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setIsLight(colorScheme === "light");
  }, [colorScheme]);
  const iconColor = isLight ? "#000000" : "#FFFFFF";

  // State to store permissions data in dropdown format
  const [permissionsData, setPermissionsData] = useState<Array<{ key: string; value: string }>>([]);
  // State to store selected permission names
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  // Fetch club permissions and set the dropdown data
  useEffect(() => {
    getClubPermissions()
      .then((permissions) => {
        // Map the response to an array of { key, value } objects
        const dropdownData = permissions.map((permission: { name: string; description: string }) => ({
          key: permission.name,
          value: permission.name,
        }));
        setPermissionsData(dropdownData);
      })
      .catch((error) => {
        console.error("Error fetching club permissions:", error);
        Alert.alert("Error", "Failed to load club permissions");
      });
  }, []);

  const handleDismissPress = () => {
    router.dismiss();
  };

  const handleInfoPress = () => {
    router.navigate("/(tabs)/clubs/(role)/InfoRole");
  };

  useEffect(() => {
    navigation.setOptions({
      headerLeft: () => (
        <Pressable onPress={handleDismissPress}>
          <Icon
            name="close"
            size={30}
            color={iconColor}
            style={{ marginLeft: "auto", marginRight: 15 }}
          />
        </Pressable>
      ),
      headerRight: () => (
        <Pressable onPress={handleInfoPress}>
          <Icon
            name="info"
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
      <View className="items-center">
        <Heading text={t("createClub")} />
        <MultiDropdown
          setSelected={setSelectedPermissions}
          values={permissionsData}
          placeholder={t("selectPermissions_placeholder")}
          notFound={t("selectPermissions_notFound")}
          searchPlaceholderText={t("selectPermissions_searchPlaceholder")}
          useSections={false}
          confirmButtonText={t("selectPermissions_confirmButton")}
        />
        <DefaultButton text={t("create")} onPress={() => console.log(selectedPermissions)} />
      </View>
    </ScrollView>
  );
};

export default AddRole;
