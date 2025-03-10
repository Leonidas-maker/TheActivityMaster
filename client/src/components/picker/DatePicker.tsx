import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, TouchableWithoutFeedback, Platform, useColorScheme } from 'react-native';
import DateTimePicker, { DateTimePickerEvent, DateTimePickerAndroid } from '@react-native-community/datetimepicker';
import DefaultButton from '../buttons/DefaultButton';
import DefaultText from '../textFields/DefaultText';

interface InlineDatePopoverProps {
    minimumDate?: Date;
    maximumDate?: Date;
    onClose: (selectedDate: Date) => void;
}

interface DatePickerTriggerProps {
    selectedDate: Date;
    onPress: () => void;
}

export const InlineDatePopover: React.FC<InlineDatePopoverProps> = ({ minimumDate, maximumDate, onClose }) => {
    const [date, setDate] = useState(new Date());

    // Build an object for optional date constraints. Only add if provided.
    const pickerProps = {
        ...(minimumDate ? { minimumDate } : {}),
        ...(maximumDate ? { maximumDate } : {})
    };

    // On Android, use the imperative API to open the native date picker dialog
    useEffect(() => {
        if (Platform.OS === 'android') {
            DateTimePickerAndroid.open({
                value: date,
                ...pickerProps,
                onChange: (event: DateTimePickerEvent, selectedDate?: Date) => {
                    if (event.type === 'set' && selectedDate) {
                        // When the user sets a date, pass the selected date
                        onClose(selectedDate);
                    } else if (event.type === 'dismissed') {
                        // When the native cancel button is pressed, pass back the original date
                        onClose(date);
                    }
                },
                mode: 'date',
                display: 'default',
                is24Hour: true,
            });
        }
    }, []);

    // Render nothing on Android because the native dialog is used
    if (Platform.OS === 'android') {
        return null;
    }

    // For iOS, use the inline popover as before
    const handleDateChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
        if (selectedDate) {
            setDate(selectedDate);
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
        <TouchableWithoutFeedback onPress={() => onClose(date)}>
            <View
                // Container covering the full screen
                className="absolute top-0 left-0 right-0 bottom-0 flex items-center justify-center"
                style={{ zIndex: 1000, elevation: 20, backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
            >
                {/* Inner TouchableWithoutFeedback prevents propagation of touches from the modal content */}
                <TouchableWithoutFeedback onPress={() => { }}>
                    <View className="bg-light_secondary dark:bg-dark_secondary p-4 rounded-xl shadow-lg">
                        <Text className="text-lg text-black dark:text-white font-bold mb-2 text-center">Select Date</Text>
                        <DateTimePicker
                            value={date}
                            mode="date"
                            display="spinner"
                            onChange={handleDateChange}
                            style={{ width: '100%' }}
                            themeVariant={themeVariant}
                            {...pickerProps}
                        />
                        <View className='justify-center flex-row'>
                            <DefaultButton
                                text="Select"
                                onPress={() => onClose(date)}
                            />
                        </View>
                    </View>
                </TouchableWithoutFeedback>
            </View>
        </TouchableWithoutFeedback>
    );
};

export const DatePickerTrigger: React.FC<DatePickerTriggerProps> = ({ selectedDate, onPress }) => {
    // Format the date as DD.MM.YYYY
    const formatDate = (date: Date) => {
        const day = date.getDate();
        const month = date.getMonth() + 1;
        const year = date.getFullYear();
        return `${day.toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${year}`;
    };

    return (
        <TouchableOpacity className="justify-center items-center bg-light_secondary dark:bg-dark_secondary w-3/4 m-2 p-4 rounded-xl shadow-lg" onPress={onPress}>
            <DefaultText text={formatDate(selectedDate)} />
        </TouchableOpacity>
    );
};
