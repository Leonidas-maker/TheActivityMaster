import React, { useState, useEffect } from 'react';
import DateTimePicker, { DateType, getDefaultStyles } from 'react-native-ui-datepicker';
import { ScrollView, View, Pressable, useColorScheme } from 'react-native';
import { useRouter, useNavigation, useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import Icon from "react-native-vector-icons/MaterialIcons";

const AddSession = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t, i18n } = useTranslation("clubs");
    const { club_id, program_id } = useLocalSearchParams();

    let tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const defaultStyles = getDefaultStyles();
    const [startDate, setStartDate] = useState<DateType>();
    const [endDate, setEndDate] = useState<DateType>();


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

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <DateTimePicker
                mode="range"
                startDate={startDate}
                endDate={endDate}
                onChange={({ startDate, endDate }) => {
                    setStartDate(startDate);
                    setEndDate(endDate);
                }}
                styles={defaultStyles}
                firstDayOfWeek={1}
                minDate={tomorrow}
                timePicker={true}
                navigationPosition="around"
                locale={i18n.language}
            />
        </ScrollView>
    );
}

export default AddSession;
