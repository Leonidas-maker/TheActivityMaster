// ManageTrainer.tsx
import React, { useState, useEffect } from "react";
import { ScrollView, View, TouchableWithoutFeedback, Keyboard, KeyboardAvoidingView, Platform, useColorScheme, Pressable } from "react-native";
import DefaultButton from "@/src/components/buttons/DefaultButton";
import Heading from "@/src/components/textFields/Heading";
import MultiDropdown from "@/src/components/dropdown/MultiDropdown";
import Toast from "react-native-toast-message";
import DefaultToast from "@/src/components/defaultToast/DefaultToast";
import { useTranslation } from "react-i18next";
import { useRouter, useNavigation, useLocalSearchParams } from "expo-router";
import { getEmployees } from "@/src/services/club/employeeService";
import { getTrainers, addTrainer, removeTrainer } from "@/src/services/club/programTrainerService";
import Icon from "react-native-vector-icons/MaterialIcons";

const ManageTrainer = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation("clubs");
    const { club_id, program_id } = useLocalSearchParams();

    // State for storing formatted employee options for the dropdown
    const [employees, setEmployees] = useState<{ key: string; value: string }[]>([]);
    // State for storing the initial list of trainer IDs (from getTrainers)
    const [initialTrainers, setInitialTrainers] = useState<string[]>([]);
    // State for the currently selected trainer IDs in the dropdown
    const [selectedTrainers, setSelectedTrainers] = useState<string[]>([]);
    // Loading state until both employees and trainers are fetched
    const [loading, setLoading] = useState(true);

    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const iconColor = isLight ? "#000000" : "#FFFFFF";

    const handleDismissPress = () => {
        router.dismiss();
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
        });
    }, [navigation, iconColor]);

    // Fetch the employees from the employee service
    useEffect(() => {
        getEmployees(club_id)
            .then((data) => {
                // The service returns an object with several properties containing arrays,
                // so we flatten all the arrays into one.
                const employeesArray = Object.values(data).flat();
                // Format each employee as "FirstName LastName (user@example.com)"
                const formattedEmployees = employeesArray.map((emp: any) => ({
                    key: emp.id,
                    value: `${emp.first_name} ${emp.last_name} (${emp.email})`
                }));
                setEmployees(formattedEmployees);
            })
            .catch((error) => {
                console.error("Error fetching employees:", error);
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            });
    }, [club_id, t]);

    // Fetch the current trainers and initialize the dropdown selection
    useEffect(() => {
        getTrainers(club_id, program_id)
            .then((data: any[]) => {
                const trainerIds = data.map(trainer => trainer.id);
                setInitialTrainers(trainerIds);
                setSelectedTrainers(trainerIds);
            })
            .catch((error) => {
                console.error("Error fetching trainers:", error);
                Toast.show({
                    type: "error",
                    text1: t("roleManageError"),
                    text2: t("roleManageErrorDescription")
                });
            })
            .finally(() => {
                setLoading(false);
            });
    }, [club_id, program_id, t]);

    // Handler for when the user confirms the changes
    const handleConfirm = async () => {
        // Determine which trainer IDs were added and which were removed
        const added = selectedTrainers.filter(id => !initialTrainers.includes(id));
        const removed = initialTrainers.filter(id => !selectedTrainers.includes(id));

        try {
            // Process each addition individually
            for (const id of added) {
                await addTrainer(club_id, program_id, id);
            }
            // Process each removal individually
            for (const id of removed) {
                await removeTrainer(club_id, program_id, id);
            }
            // If all calls succeed, update the initial state
            setInitialTrainers(selectedTrainers);
            router.dismiss();
        } catch (error) {
            console.error("Error updating trainers:", error);
            Toast.show({
                type: "error",
                text1: t("roleManageError"),
                text2: t("roleManageErrorDescription")
            });
            // Revert the selection to the previous state
            setSelectedTrainers(initialTrainers);
        }
    };

    if (loading) {
        return null;
    }

    return (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">
            <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
                <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
                    <View className="items-center">
                        <View className="py-4">
                            <Heading text={t("manage_trainers_heading")} />
                        </View>
                        <MultiDropdown
                            setSelected={setSelectedTrainers}
                            values={employees}
                            placeholder={t("select_trainers_placeholder")}
                            notFound={t("no_employees_found")}
                            searchPlaceholderText={t("search_employees_placeholder")}
                            useSections={false}
                            confirmButtonText={t("selectPermissions_confirmButton")}
                            initialSelected={selectedTrainers}
                        />
                        <View className="w-full items-center mt-4">
                            <DefaultButton text={t("update_trainer_btn")} onPress={handleConfirm} />
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
            <DefaultToast />
        </KeyboardAvoidingView>
    );
};

export default ManageTrainer;