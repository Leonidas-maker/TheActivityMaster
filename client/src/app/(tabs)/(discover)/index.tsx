import React, { useEffect, useState, useRef } from "react";
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  Modal,
  TouchableOpacity,
  TextInput,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
  TouchableWithoutFeedback,
  Keyboard,
  useColorScheme,
  Switch
} from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import Icon from "react-native-vector-icons/MaterialIcons";
import Toast from "react-native-toast-message";
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import Subheading from "@/src/components/textFields/Subheading";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import DefaultTextFieldInput from "@/src/components/textInputs/DefaultTextInput";
import Carousel, { ICarouselInstance, Pagination } from "react-native-reanimated-carousel";
import Dropdown from "@/src/components/dropdown/Dropdown";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import { useSharedValue } from "react-native-reanimated";

import { getClubs } from "@/src/services/club/clubService";
import { searchPrograms, getProgramCategories } from "@/src/services/club/programService";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";

// Define TypeScript interfaces for Club and Program
interface Club {
  name: string;
  description: string;
  address: {
    street: string;
    postal_code: string;
    city: string;
    state: string;
    country: string;
  };
  id: string;
  is_deleted: boolean;
}

interface Program {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  pricing_model: string;
  capacity: number;
  membership_required: boolean;
  club_id: string;
  categories: number[];
  status: string;
}

// Main Discover Page component
export default function DiscoverPage() {
  const { t, i18n } = useTranslation("discover");
  const router = useRouter();
  const screenWidth = Dimensions.get("window").width;

  /***
   * State for Clubs
   */
  const [clubs, setClubs] = useState<Club[]>([]);
  const [loadingClubs, setLoadingClubs] = useState(false);
  const clubsCarouselRef = useRef<ICarouselInstance>(null);

  /***
   * State for Programs
   * programsByCategory maps a category key (as string) to a list of programs
   */
  const [programsByCategory, setProgramsByCategory] = useState<{ [key: string]: Program[] }>({});
  const [loadingPrograms, setLoadingPrograms] = useState(false);

  /***
   * State for Program Categories (available options from API)
   */
  const [programCategories, setProgramCategories] = useState<{ key: string; value: string }[]>([]);
  // This state holds the categories used to fetch programs. If user does not select any in filter, we pick 5 random ones.
  const [selectedProgramCategories, setSelectedProgramCategories] = useState<string[]>([]);
  const [randomCategoriesEnabled, setRandomCategoriesEnabled] = useState<boolean>(true);

  const [isLight, setIsLight] = useState(false);
  const colorScheme = useColorScheme();
  useEffect(() => {
    setIsLight(colorScheme === "light");
  }, [colorScheme]);
  const iconColor = isLight ? "#000000" : "#FFFFFF";

  /***
   * Filter Modal States
   * For clubs: city
   * For programs: minPrice, maxPrice, sessionType and multi-select program categories
   */
  const [modalVisible, setModalVisible] = useState(false);
  const [filterCity, setFilterCity] = useState("");
  const [filterMinPrice, setFilterMinPrice] = useState("");
  const [filterMaxPrice, setFilterMaxPrice] = useState("");
  const [filterSessionType, setFilterSessionType] = useState("");
  const [filterProgramCategories, setFilterProgramCategories] = useState<string[]>([]);
  // New states for applied filters
  const [appliedFilterCity, setAppliedFilterCity] = useState("");
  const [appliedFilterMinPrice, setAppliedFilterMinPrice] = useState("");
  const [appliedFilterMaxPrice, setAppliedFilterMaxPrice] = useState("");
  const [appliedFilterSessionType, setAppliedFilterSessionType] = useState("");
  const [appliedFilterProgramCategories, setAppliedFilterProgramCategories] = useState<string[]>([]);

  const progressClubs = useSharedValue(0);
  const refClubs = useRef<ICarouselInstance>(null);
  const progressPrograms = useSharedValue(0);
  const refPrograms = useRef<ICarouselInstance>(null);

  const dotStyle = {
    width: 10,
    height: 4,
    backgroundColor: colorScheme === "dark" ? "#cccccc" : "#444444",
  };
  const activeDotStyle = {
    overflow: "hidden" as "hidden",
    backgroundColor: colorScheme === "dark" ? "#ED2A1D" : "#DE1A1A",
  };
  const containerStyle = {
    gap: 5,
  };

  /***
   * Function to fetch clubs with infinite scroll support
   */
  const fetchClubs = async () => {
    setLoadingClubs(true);
    try {
      // TODO: Add dynamic loading
      const data: Club[] = await getClubs(1, 50, appliedFilterCity);
      setClubs(data);
    } catch (error) {
      Toast.show({
        type: "error",
        text1: t("errorFetchingClubs"),
        text2: t("pleaseTryAgain")
      });
    } finally {
      setLoadingClubs(false);
    }
  };

  /***
   * Function to fetch program categories from API
   */
  const fetchProgramCategories = async () => {
    try {
      const categoriesResponse = await getProgramCategories(i18n.language);
      const categoriesOptions = categoriesResponse.map((category: { id: number; name: string; description: string }) => ({
        key: category.id.toString(),
        value: category.name
      }));
      setProgramCategories(categoriesOptions);
      // If no filter is applied, pick 5 random categories (or all if less than 5)
      if (randomCategoriesEnabled) {
        const randomCats = [...categoriesOptions]
          .sort(() => Math.random() - 0.5)
          .slice(0, 5)
          .map(cat => cat.key);
        setSelectedProgramCategories(randomCats);
      } else {
        setSelectedProgramCategories(appliedFilterProgramCategories);
      }
    } catch (error) {
      Toast.show({
        type: "error",
        text1: t("errorFetchingCategories"),
        text2: t("pleaseTryAgain")
      });
    }
  };

  /***
   * Function to fetch programs for each selected category
   */
  const fetchProgramsForCategories = async () => {
    setLoadingPrograms(true);
    const newProgramsByCategory: { [key: string]: Program[] } = {};
    try {
      // For each selected category, call searchPrograms
      await Promise.all(
        selectedProgramCategories.map(async (catKey) => {
          const categoryId = parseInt(catKey, 10);
          if (isNaN(categoryId)) {
            Toast.show({
              type: "error",
              text1: t("errorInvalidCategory"),
              text2: t("pleaseTryAgain")
            });
            newProgramsByCategory[catKey] = [];
            return;
          }
          try {
            const programs: Program[] = await searchPrograms(
              null,
              1,
              10,
              categoryId,
              appliedFilterMinPrice ? Number(appliedFilterMinPrice) * 100 : null,
              appliedFilterMaxPrice ? Number(appliedFilterMaxPrice) * 100 : null,
              appliedFilterSessionType || null
            );
            newProgramsByCategory[catKey] = programs;
          } catch (error) {
            Toast.show({
              type: "error",
              text1: t("errorFetchingPrograms"),
              text2: t("pleaseTryAgain")
            });
            newProgramsByCategory[catKey] = [];
          }
        })
      );
      setProgramsByCategory(newProgramsByCategory);
    } catch (error) {
      // Global error catch
      Toast.show({
        type: "error",
        text1: t("errorFetchingPrograms"),
        text2: t("pleaseTryAgain")
      });
    } finally {
      setLoadingPrograms(false);
    }
  };

  // Initial fetch on mount and when filters change
  useEffect(() => {
    setClubs([]);
    fetchClubs();
    fetchProgramCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appliedFilterCity, appliedFilterMinPrice, appliedFilterMaxPrice, appliedFilterSessionType, appliedFilterProgramCategories, i18n.language]);

  // When selected program categories changes, fetch programs
  useEffect(() => {
    if (selectedProgramCategories.length > 0) {
      fetchProgramsForCategories();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProgramCategories, appliedFilterMinPrice, appliedFilterMaxPrice, appliedFilterSessionType]);

  /***
   * Handler for applying filters from modal
   */
  const applyFilters = () => {
    setAppliedFilterCity(filterCity);
    setAppliedFilterMinPrice(filterMinPrice);
    setAppliedFilterMaxPrice(filterMaxPrice);
    setAppliedFilterSessionType(filterSessionType);
    if (randomCategoriesEnabled) {
      setAppliedFilterProgramCategories([]);
    } else {
      setAppliedFilterProgramCategories(filterProgramCategories);
    }
    setModalVisible(false);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1 bg-light_primary dark:bg-dark_primary"
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView contentContainerStyle={{ flexGrow: 1, paddingBottom: 100 }}>
          {/* Header with Welcome and Filter Icon */}
          <View className="flex-row items-center justify-between p-4 bg-light_primary dark:bg-dark_primary">
            <Heading text={t("welcomeBack") || "Welcome Back"} />
            <TouchableOpacity onPress={() => setModalVisible(true)}>
              <Icon name="filter-list" size={28} color={iconColor} />
            </TouchableOpacity>
          </View>


          {/* Clubs Section */}
          <View className="p-4">
            <Heading text={t("clubs")} />
            {loadingClubs && clubs.length === 0 ? (
              <ActivityIndicator size="large" color={iconColor} />
            ) : clubs.length === 0 ? (
              <DefaultText text={t("noClubsAvailable") || "No clubs available."} />
            ) : (
              <View>
                <Carousel
                  ref={refClubs}
                  width={screenWidth * 0.9}
                  height={180}
                  data={clubs}
                  scrollAnimationDuration={1000}
                  mode="parallax"
                  modeConfig={{
                    parallaxScrollingScale: 0.9,
                    parallaxScrollingOffset: 50,
                  }}
                  onProgressChange={progressClubs}
                  renderItem={({ item, index }) => (
                    <TouchableOpacity
                      key={index}
                      className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                      onPress={() => {
                        // Navigate to Club Page
                        router.navigate(`/(tabs)/(discover)/(view)/ClubPage?club_id=${item.id}`);
                      }}
                    >
                      <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                        <DefaultText text={t("clubPicturePlaceholder") || "Club Picture Placeholder"} />
                      </View>
                      <DefaultText text={item.name} />
                      <DefaultText text={item.description} />
                      <DefaultText text={`${item.address.city}, ${item.address.country}`} />
                    </TouchableOpacity>
                  )}
                />
                {/* Pagination Dots for Clubs Carousel */}
                <Pagination.Basic
                  progress={progressClubs}
                  data={clubs}
                  dotStyle={dotStyle}
                  activeDotStyle={activeDotStyle}
                  containerStyle={containerStyle}
                  horizontal
                  onPress={(index) => {
                    refClubs.current?.scrollTo({ count: index - progressClubs.value, animated: true });
                  }}
                />
              </View>
            )}
          </View>

          {/* Programs Section */}
          <View className="p-4">
            <Heading text={t("programs")} />
            {loadingPrograms ? (
              <ActivityIndicator size="large" color="#000" />
            ) : (Object.keys(programsByCategory).length === 0 ||
              Object.keys(programsByCategory).every(
                (key) => programsByCategory[key].length === 0
              )) ? (
              <Subheading text={t("noProgramsAvailable")} />
            ) : (
              Object.keys(programsByCategory).map((catKey, idx) => {
                // Find category name from programCategories
                const category = programCategories.find((cat) => cat.key === catKey);
                return (
                  <View key={catKey} className="mb-8">
                    <Subheading text={category ? category.value : `Category ${catKey}`} />
                    {programsByCategory[catKey].length === 0 ? (
                      <DefaultText text={t("noProgramsForCategory")} />
                    ) : (
                      <View>
                        <Carousel
                          ref={refPrograms}
                          width={screenWidth * 0.9}
                          height={180}
                          data={programsByCategory[catKey]}
                          scrollAnimationDuration={1000}
                          mode="parallax"
                          modeConfig={{
                            parallaxScrollingScale: 0.9,
                            parallaxScrollingOffset: 50,
                          }}
                          onProgressChange={progressPrograms}
                          renderItem={({ item, index }) => (
                            <TouchableOpacity
                              key={index}
                              className="mx-2 bg-light_secondary dark:bg-dark_secondary rounded-xl p-4"
                              onPress={() => {
                                // Navigate to Program Page
                                router.navigate(`/(tabs)/(discover)/(view)/ProgramPage?club_id=${item.club_id}&program_id=${item.id}`);
                              }}
                            >
                              <View className="w-full h-24 bg-gray-200 dark:bg-gray-600 justify-center items-center mb-2 rounded-xl">
                                <DefaultText text={t("programPicturePlaceholder") || "Program Picture Placeholder"} />
                              </View>
                              <DefaultText text={item.name} />
                              <DefaultText text={item.description} />
                            </TouchableOpacity>
                          )}
                        />
                        <Pagination.Basic
                          progress={progressPrograms}
                          data={programsByCategory[catKey]}
                          dotStyle={dotStyle}
                          activeDotStyle={activeDotStyle}
                          containerStyle={containerStyle}
                          horizontal
                          onPress={(index) => {
                            refPrograms.current?.scrollTo({ count: index - progressPrograms.value, animated: true });
                          }}
                        />
                      </View>
                    )}
                  </View>
                );
              })
            )}
          </View>

          {/* Filter Modal */}
          <Modal
            visible={modalVisible}
            transparent
            animationType="slide"
            onRequestClose={() => setModalVisible(false)}
          >
            <TouchableOpacity
              activeOpacity={1}
              onPress={() => setModalVisible(false)}
              className="flex-1 justify-center items-center bg-black/50"
            >
              <TouchableOpacity
                activeOpacity={1}
                onPress={(e) => e.stopPropagation()}
                className="bg-light_primary dark:bg-dark_primary p-6 rounded-lg w-3/4"
              >
                <Text className="text-lg mb-2 text-black dark:text-white">
                  {t("filterOptions") || "Filter Options"}
                </Text>

                {/* Club Filter: City */}
                <View className="mb-4">
                  <Text className="text-black dark:text-white">{t("city") || "City"}</Text>
                  <View className="justify-center items-center">
                    <DefaultTextFieldInput
                      value={filterCity}
                      onChangeText={setFilterCity}
                      placeholder={t("enterCity") || "Enter city"}
                    />
                  </View>
                </View>

                {/* Program Filters: Min Price, Max Price, Session Type */}
                <View className="mb-4">
                  <Text className="text-black dark:text-white">{t("minPrice") || "Min Price"}</Text>
                  <View className="justify-center items-center">
                    <DefaultTextFieldInput
                      value={filterMinPrice}
                      onChangeText={setFilterMinPrice}
                      placeholder={t("minPricePlaceholder") || "Min Price"}
                      keyboardType="numeric"
                    />
                  </View>
                </View>
                <View className="mb-4">
                  <Text className="text-black dark:text-white">{t("maxPrice") || "Max Price"}</Text>
                  <View className="justify-center items-center">
                    <DefaultTextFieldInput
                      value={filterMaxPrice}
                      onChangeText={setFilterMaxPrice}
                      placeholder={t("maxPricePlaceholder") || "Max Price"}
                      keyboardType="numeric"
                    />
                  </View>
                </View>
                <View className="mb-4">
                  <Text className="text-black dark:text-white">{t("sessionType") || "Session Type"}</Text>
                  {/* Simple dropdown using TouchableOpacity for session type */}
                  <View className="mb-4">
                    <Text className="text-black dark:text-white">
                      {t("sessionType") || "Session Type"}
                    </Text>
                    <View className="justify-center items-center">
                      <Dropdown
                        setSelected={setFilterSessionType}
                        values={[
                          { key: "", value: t("selectSessionType_placeholder") || "Select Session Type" },
                          { key: "course", value: t("course") || "Course" },
                          { key: "event", value: t("event") || "Event" }
                        ]}
                        defaultOption={{
                          key: filterSessionType,
                          value: filterSessionType ? t(filterSessionType) : (t("selectSessionType_placeholder") || "Select Session Type")
                        }}
                        placeholder={t("selectSessionType_placeholder") || "Select Session Type"}
                        save="key"
                      />
                    </View>
                  </View>
                </View>

                {/* Program Categories Multi-select */}
                <View className="mb-4">
                  <Text className="text-black dark:text-white">{t("programCategories") || "Program Categories (Select up to 5)"}</Text>
                  {/* Program Categories Multi-select with Random Toggle */}
                  <View className="mb-4">
                    <View className="flex-row items-center justify-between mb-2">
                      <Text className="text-black dark:text-white">
                        {t("useRandomCategories") || "Use 5 Random Categories"}
                      </Text>
                      <Switch
                        value={randomCategoriesEnabled}
                        onValueChange={setRandomCategoriesEnabled}
                      />
                    </View>
                    {!randomCategoriesEnabled && (
                      <View className="justify-center items-center">
                        <MultiDropdown
                          setSelected={setFilterProgramCategories}
                          values={programCategories}
                          searchPlaceholderText={t("searchCategories")}
                          confirmButtonText={t("confirm")}
                          placeholder={t("programCategories") || "Program Categories (Select up to 5)"}
                          maxSelectedItems={5}
                          save="key"
                          useSections={false}
                        />
                      </View>
                    )}
                  </View>
                </View>

                <View className="w-full items-center justify-center">
                  <DefaultButton text={t("applyButton") || "Apply"} onPress={applyFilters} />
                </View>
              </TouchableOpacity>
            </TouchableOpacity>
          </Modal>

          {/* Toast Component */}
          <DefaultToast />
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView >
  );
}