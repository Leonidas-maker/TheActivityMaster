import React, { useState, useEffect } from "react";
import {
    View,
    ActivityIndicator,
    ScrollView,
    Modal,
    Switch,
    Text,
    TouchableOpacity,
    TextInput,
    KeyboardAvoidingView,
    TouchableWithoutFeedback,
    Keyboard,
    Platform,
    useColorScheme,
} from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import Subheading from "@/src/components/textFields/Subheading";
import { useTranslation } from "react-i18next";
import SearchBar from "react-native-platform-searchbar";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useRouter } from "expo-router";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import Toast from "react-native-toast-message";
import DefaultButton from "@/src/components/buttons/DefaultButton";

import { searchClubs } from "@/src/services/club/clubService";
import { searchPrograms } from "@/src/services/club/programService";

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
    name: string;
    description: string;
    price: number;
    currency: string;
    pricing_model: string;
    capacity: number;
    membership_required: boolean;
    club_id: string;
    id: string;
    categories: number[];
    status: string;
}

export default function SearchScreen() {
    const { t } = useTranslation("search");
    const router = useRouter();

    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    // Search query
    const [query, setQuery] = useState("");
    // Track which sections to show
    const [showClubs, setShowClubs] = useState(true);
    const [showPrograms, setShowPrograms] = useState(true);
    // Search results
    const [clubs, setClubs] = useState<Club[]>([]);
    const [programs, setPrograms] = useState<Program[]>([]);
    // Pagination
    const [clubsPage, setClubsPage] = useState(1);
    const [programsPage, setProgramsPage] = useState(1);
    // Loading indicator
    const [loading, setLoading] = useState(false);
    // Modal visibility
    const [modalVisible, setModalVisible] = useState(false);
    // Has user performed at least one search?
    const [hasSearched, setHasSearched] = useState(false);

    // Page size state (between 1 and 50) and its text representation
    const [pageSize, setPageSize] = useState(10);
    const [pageSizeText, setPageSizeText] = useState("10");

    const resultsFound = (showClubs && clubs.length > 0) || (showPrograms && programs.length > 0);

    const handleSearch = async () => {
        if (!query.trim()) {
            Toast.show({
                type: "info",
                text1: t("noInputError"),
                text2: t("noInputErrorDescription"),
            });
            return;
        }
        setHasSearched(true);
        setLoading(true);
        try {
            if (showClubs) {
                const clubsData = await searchClubs(query, 1, pageSize);
                setClubs(clubsData);
                setClubsPage(1);
            } else {
                setClubs([]);
            }
            if (showPrograms) {
                const programsData = await searchPrograms(query, 1, pageSize);
                setPrograms(programsData);
                setProgramsPage(1);
            } else {
                setPrograms([]);
            }
        } catch (error) {
            console.error(t("searchError"), error);
        } finally {
            setLoading(false);
        }
    };

    const handleApplyFilter = () => {
        setModalVisible(false);
    };

    /**
     * Renders a simple pagination bar using icons.
     * Pagination is visible only if the results count equals (or exceeds) the page size.
     * Displays the current page number in the center.
     */
    const renderPagination = (
        currentPage: number,
        onPageChange: (page: number) => Promise<void>,
        resultsCount: number
    ) => {
        // Show pagination only if there are as many items as the page size
        if (resultsCount < pageSize) return null;

        return (
            <View className="flex-row justify-center items-center space-x-4 mt-4">
                <TouchableOpacity
                    onPress={() => {
                        if (currentPage > 1) onPageChange(currentPage - 1);
                    }}
                    disabled={currentPage === 1}
                    className="px-2 py-2"
                >
                    <Icon name="arrow-back" size={24} color={iconColor} />
                </TouchableOpacity>
                <Text style={{ color: iconColor }}>{currentPage}</Text>
                <TouchableOpacity
                    onPress={() => onPageChange(currentPage + 1)}
                    className="px-2 py-2"
                >
                    <Icon name="arrow-forward" size={24} color={iconColor} />
                </TouchableOpacity>
            </View>
        );
    };

    // Update programs without affecting clubs
    const handleProgramsPageChange = async (page: number) => {
        if (page > programsPage) {
            // Next page requested
            setLoading(true);
            try {
                const programsData = await searchPrograms(query, page, pageSize);
                if (!programsData || programsData.length === 0) {
                    Toast.show({ type: 'info', text1: t('noMoreResults') });
                    // Do not update page if no results
                } else {
                    setPrograms(programsData);
                    setProgramsPage(page);
                }
            } catch (error) {
                console.error(t('searchError'), error);
            } finally {
                setLoading(false);
            }
        } else if (page < programsPage) {
            // Previous page requested
            setLoading(true);
            try {
                const programsData = await searchPrograms(query, page, pageSize);
                setPrograms(programsData);
                setProgramsPage(page);
            } catch (error) {
                console.error(t('searchError'), error);
            } finally {
                setLoading(false);
            }
        }
    };

    // Update handleClubsPageChange to check for next page results before updating:
    const handleClubsPageChange = async (page: number) => {
        if (page > clubsPage) {
            // Next page requested
            setLoading(true);
            try {
                const clubsData = await searchClubs(query, page, pageSize);
                if (!clubsData || clubsData.length === 0) {
                    Toast.show({ type: "info", text1: t("noMoreResults") });
                    // Do not update page if no results
                } else {
                    setClubs(clubsData);
                    setClubsPage(page);
                }
            } catch (error) {
                console.error(t("searchError"), error);
            } finally {
                setLoading(false);
            }
        } else if (page < clubsPage) {
            // Previous page requested
            setLoading(true);
            try {
                const clubsData = await searchClubs(query, page, pageSize);
                setClubs(clubsData);
                setClubsPage(page);
            } catch (error) {
                console.error(t("searchError"), error);
            } finally {
                setLoading(false);
            }
        }
    };

    const dismissModal = () => {
        setModalVisible(false);
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            className="flex-1"
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <View className="flex-1 bg-light_primary dark:bg-dark_primary">
                    {/* Header with filter icon, search bar, and search icon */}
                    <View className="p-4 bg-light_primary dark:bg-dark_primary">
                        <View className="flex-row items-center mt-2">
                            <TouchableOpacity
                                onPress={() => setModalVisible(true)}
                                className="mr-2"
                            >
                                <Icon name="filter-list" size={28} color={iconColor} />
                            </TouchableOpacity>

                            <View className="flex-1">
                                <SearchBar
                                    value={query}
                                    onChangeText={setQuery}
                                    placeholder={t("searchPlaceholder")}
                                    theme={isLight ? "light" : "dark"}
                                >
                                    {loading ? (
                                        <ActivityIndicator style={{ marginRight: 10 }} />
                                    ) : undefined}
                                </SearchBar>
                            </View>

                            <TouchableOpacity onPress={handleSearch} className="ml-2">
                                <Icon name="search" size={28} color={iconColor} />
                            </TouchableOpacity>
                        </View>
                    </View>

                    <ScrollView className="flex-1">
                        {/* Clubs section */}
                        {hasSearched && showClubs && (
                            <View className="mb-4 px-4">
                                <Subheading text={t("clubs")} />
                                {clubs.length === 0 ? (
                                    <View className="mt-2">
                                        <DefaultText text={t("noClubsFound")} />
                                    </View>
                                ) : (
                                    <>
                                        <View className="space-y-2 mt-2">
                                            {clubs.map((club) => (
                                                <TouchableOpacity
                                                    key={club.id}
                                                    onPress={() =>
                                                        router.push({
                                                            pathname: "/",
                                                            params: { itemId: club.id },
                                                        })
                                                    }
                                                    className="bg-white dark:bg-gray-800 p-4 m-2 rounded-lg shadow-md"
                                                >
                                                    <DefaultText text={club.name} />
                                                    <DefaultText text={club.description} />
                                                    <DefaultText
                                                        text={`${club.address.city}, ${club.address.country}`}
                                                    />
                                                </TouchableOpacity>
                                            ))}
                                        </View>
                                        {renderPagination(clubsPage, handleClubsPageChange, clubs.length)}
                                    </>
                                )}
                            </View>
                        )}

                        {/* Programs section */}
                        {hasSearched && showPrograms && (
                            <View className="mb-4 px-4">
                                <Subheading text={t("programs")} />
                                {programs.length === 0 ? (
                                    <View className="mt-2">
                                        <DefaultText text={t("noProgramsFound")} />
                                    </View>
                                ) : (
                                    <>
                                        <View className="space-y-2 mt-2">
                                            {programs.map((program) => (
                                                <TouchableOpacity
                                                    key={program.id}
                                                    onPress={() =>
                                                        router.push({
                                                            pathname: "/",
                                                            params: { itemId: program.id },
                                                        })
                                                    }
                                                    className="bg-white dark:bg-gray-800 p-4 m-2 rounded-lg shadow-md"
                                                >
                                                    <DefaultText text={program.name} />
                                                    <DefaultText text={program.description} />
                                                    <DefaultText
                                                        text={`${(program.price / 100).toFixed(2)} ${program.currency}`}
                                                    />
                                                </TouchableOpacity>
                                            ))}
                                        </View>
                                        {renderPagination(programsPage, handleProgramsPageChange, programs.length)}
                                    </>
                                )}
                            </View>
                        )}
                    </ScrollView>

                    {/* Modal for filter options */}
                    <Modal
                        visible={modalVisible}
                        transparent
                        animationType="slide"
                        onRequestClose={dismissModal}
                    >
                        <TouchableOpacity
                            activeOpacity={1}
                            onPress={dismissModal}
                            className="flex-1 justify-center items-center bg-black/50"
                        >
                            <TouchableOpacity
                                activeOpacity={1}
                                onPress={(e) => e.stopPropagation()}
                                className="bg-white dark:bg-gray-800 p-6 rounded-lg w-3/4"
                            >
                                <Text className="text-lg mb-2 text-black dark:text-white">
                                    {t("filterOptions")}
                                </Text>
                                <View className="flex-row items-center justify-between mb-2">
                                    <Text className="text-black dark:text-white">
                                        {t("showClubs")}
                                    </Text>
                                    <Switch value={showClubs} onValueChange={setShowClubs} />
                                </View>
                                <View className="flex-row items-center justify-between mb-2">
                                    <Text className="text-black dark:text-white">
                                        {t("showPrograms")}
                                    </Text>
                                    <Switch value={showPrograms} onValueChange={setShowPrograms} />
                                </View>
                                {/* Page Size Option */}
                                <View className="flex-row items-center justify-between mb-4">
                                    <Text className="text-black dark:text-white">
                                        {t("pageSize")}
                                    </Text>
                                    <View className="flex-row items-center">
                                        <TouchableOpacity
                                            onPress={() => {
                                                const newVal = Math.max(1, pageSize - 1);
                                                setPageSize(newVal);
                                                setPageSizeText(newVal.toString());
                                            }}
                                        >
                                            <Icon name="remove" size={24} color={iconColor} />
                                        </TouchableOpacity>
                                        <TextInput
                                            value={pageSizeText}
                                            onChangeText={(value) => setPageSizeText(value)}
                                            onBlur={() => {
                                                const newValue = parseInt(pageSizeText, 10);
                                                if (
                                                    !isNaN(newValue) &&
                                                    newValue >= 1 &&
                                                    newValue <= 50
                                                ) {
                                                    setPageSize(newValue);
                                                    setPageSizeText(newValue.toString());
                                                } else {
                                                    setPageSizeText(pageSize.toString());
                                                }
                                            }}
                                            keyboardType="numeric"
                                            style={{
                                                width: 40,
                                                textAlign: "center",
                                                marginHorizontal: 8,
                                                color: iconColor,
                                            }}
                                        />
                                        <TouchableOpacity
                                            onPress={() => {
                                                const newVal = Math.min(50, pageSize + 1);
                                                setPageSize(newVal);
                                                setPageSizeText(newVal.toString());
                                            }}
                                        >
                                            <Icon name="add" size={24} color={iconColor} />
                                        </TouchableOpacity>
                                    </View>
                                </View>
                                <View className="w-full items-center justify-center">
                                    <DefaultButton text={t("applyButton")} onPress={handleApplyFilter} />
                                </View>
                            </TouchableOpacity>
                        </TouchableOpacity>
                    </Modal>
                </View>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
}