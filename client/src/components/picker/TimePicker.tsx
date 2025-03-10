import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, TouchableWithoutFeedback, Platform, useColorScheme } from 'react-native';
import DateTimePicker, { DateTimePickerEvent, DateTimePickerAndroid } from '@react-native-community/datetimepicker';
import DefaultText from '../textFields/DefaultText';
import DefaultButton from '../buttons/DefaultButton';
import { useTranslation } from 'react-i18next';

interface InlineTimePopoverProps {
    onClose: (selectedTime: Date) => void;
}

interface TimePickerTriggerProps {
    selectedTime: Date;
    onPress: () => void;
}

export const InlineTimePopover: React.FC<InlineTimePopoverProps> = ({ onClose }) => {
    const [time, setTime] = useState(new Date());
    const { t } = useTranslation("clubs");

    // On Android, open the native time picker dialog using the imperative API
    useEffect(() => {
        if (Platform.OS === 'android') {
            DateTimePickerAndroid.open({
                value: time,
                onChange: (event: DateTimePickerEvent, selectedDate?: Date) => {
                    if (event.type === 'set' && selectedDate) {
                        onClose(selectedDate);
                    } else if (event.type === 'dismissed') {
                        onClose(time);
                    }
                },
                mode: 'time',
                display: 'default',
            });
        }
    }, []);

    // On Android, render nothing since the native dialog is used
    if (Platform.OS === 'android') {
        return null;
    }

    // For iOS, use the inline popover as before
    const handleTimeChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
        if (selectedDate) {
            setTime(selectedDate);
        }
    };

    const [isLight, setIsLight] = useState(false);
    const colorScheme = useColorScheme();
    useEffect(() => {
        setIsLight(colorScheme === "light");
    }, [colorScheme]);
    const themeVariant = isLight ? "light" : "dark";

    return (
        // Outer TouchableWithoutFeedback detects touches outside the modal
        <TouchableWithoutFeedback onPress={() => onClose(time)}>
            <View
                // Container covering the full screen
                className="absolute top-0 left-0 right-0 bottom-0 justify-center items-center"
                style={{ zIndex: 1000, elevation: 20, backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
            >
                {/* Inner TouchableWithoutFeedback prevents propagation of touches from the modal content */}
                <TouchableWithoutFeedback onPress={() => { }}>
                    <View className="bg-light_secondary dark:bg-dark_secondary p-4 rounded-xl shadow-lg" pointerEvents='auto'>
                        <Text className="text-lg text-black dark:text-white font-bold mb-2 text-center">{t("select_time")}</Text>
                        <DateTimePicker
                            value={time}
                            mode="time"
                            display="spinner"
                            onChange={handleTimeChange}
                            style={{ width: '100%' }}
                            themeVariant={themeVariant}
                        />
                        <View className='justify-center flex-row'>
                            <DefaultButton
                                text={t("confirm_btn")}
                                onPress={() => onClose(time)}
                            />
                        </View>
                    </View>
                </TouchableWithoutFeedback>
            </View>
        </TouchableWithoutFeedback>
    );
};

export const TimePickerTrigger: React.FC<TimePickerTriggerProps> = ({ selectedTime, onPress }) => {
    // Formats the time as hh:mm
    const formatTime = (date: Date) => {
        const hours = date.getHours();
        const minutes = date.getMinutes();
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    };

    return (
        <TouchableOpacity className="justify-center items-center bg-light_secondary dark:bg-dark_secondary w-3/4 m-2 p-4 rounded-xl shadow-lg" onPress={onPress}>
            <DefaultText text={formatTime(selectedTime)} />
        </TouchableOpacity>
    );
};
