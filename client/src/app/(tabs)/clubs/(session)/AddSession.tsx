import React, { useState, useEffect } from 'react';
import { ScrollView, View, Pressable, useColorScheme } from 'react-native';
import { useRouter, useNavigation, useLocalSearchParams } from 'expo-router';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { TimePickerTrigger, InlineTimePopover } from '@/src/components/picker/TimePicker';
import { DatePickerTrigger, InlineDatePopover } from '@/src/components/picker/DatePicker';

const AddSession = () => {
    const router = useRouter();
    const navigation = useNavigation();
    const { t } = useTranslation('clubs');
    const { club_id, program_id } = useLocalSearchParams();

    // State for time picker
    const [selectedTime, setSelectedTime] = useState(new Date());
    const [timePopoverVisible, setTimePopoverVisible] = useState(false);

    // State for date picker (using single mode in this example)
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [datePopoverVisible, setDatePopoverVisible] = useState(false);

    // State for theme (light or dark)
    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === 'light');
    }, [colorScheme]);
    const iconColor = isLight ? '#000000' : '#FFFFFF';

    // Handler to dismiss the screen
    const handleDismissPress = () => {
        router.dismiss();
    };

    // Handler when the time popover closes
    const handleTimePopoverClose = (time: Date) => {
        setSelectedTime(time);
        setTimePopoverVisible(false);
    };

    // Handler when the date popover closes
    const handleDatePopoverClose = (
        selected: Date | { startDate: Date; endDate: Date }
    ) => {
        // In single mode, selected should be a Date instance
        if (selected instanceof Date) {
            setSelectedDate(selected);
        } else {
            // Optionally, handle range mode here if needed
            // For now, if range mode is not used, you might log an error or do nothing.
        }
        setDatePopoverVisible(false);
    };

    // Set custom header with a dismiss button
    useEffect(() => {
        navigation.setOptions({
            headerLeft: () => (
                <Pressable onPress={handleDismissPress}>
                    <Icon
                        name="close"
                        size={30}
                        color={iconColor}
                        style={{ marginLeft: 'auto', marginRight: 15 }}
                    />
                </Pressable>
            ),
        });
    }, [navigation, iconColor]);

    return (
        <View className="bg-white rounded-lg w-full h-screen">
            <ScrollView
                scrollEnabled={!(timePopoverVisible || datePopoverVisible)}
                keyboardShouldPersistTaps="always"
                className="bg-light_primary dark:bg-dark_primary"
            >
                {/* Time picker trigger */}
                <TimePickerTrigger
                    selectedTime={selectedTime}
                    onPress={() => setTimePopoverVisible(true)}
                />
                {/* Date picker trigger for single date selection */}
                <DatePickerTrigger
                    selectedDate={selectedDate}
                    onPress={() => setDatePopoverVisible(true)}
                />
            </ScrollView>

            {/* Render time popover outside the ScrollView */}
            {timePopoverVisible && (
                <InlineTimePopover onClose={handleTimePopoverClose} />
            )}
            {/* Render date popover outside the ScrollView */}
            {datePopoverVisible && (
                <InlineDatePopover
                    onClose={handleDatePopoverClose}
                />
            )}
        </View>
    );
};

export default AddSession;
