import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, TouchableWithoutFeedback, Platform } from 'react-native';
import DateTimePicker, { DateTimePickerEvent, DateTimePickerAndroid } from '@react-native-community/datetimepicker';

interface InlineDatePopoverProps {
    onClose: (selectedDate: Date) => void;
}

interface DatePickerTriggerProps {
    selectedDate: Date;
    onPress: () => void;
}

export const InlineDatePopover: React.FC<InlineDatePopoverProps> = ({ onClose }) => {
    const [date, setDate] = useState(new Date());
  
    // On Android, use the imperative API to open the native date picker dialog
    useEffect(() => {
      if (Platform.OS === 'android') {
        DateTimePickerAndroid.open({
          value: date,
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
  
    // Format the date as MM/DD/YYYY
    const formatDate = (date: Date) => {
      const day = date.getDate();
      const month = date.getMonth() + 1; // Months are zero-indexed
      const year = date.getFullYear();
      return `${month.toString().padStart(2, '0')}/${day.toString().padStart(2, '0')}/${year}`;
    };
  
    return (
      // Outer TouchableWithoutFeedback detects touches outside the modal
      <TouchableWithoutFeedback onPress={() => onClose(date)}>
        <View
          // Container covering the full screen
          className="absolute top-0 left-0 right-0 bottom-0 justify-center items-center"
          style={{ zIndex: 1000, elevation: 20 }}
        >
          {/* Inner TouchableWithoutFeedback prevents propagation of touches from the modal content */}
          <TouchableWithoutFeedback onPress={() => {}}>
            <View className="bg-white p-4 rounded shadow-lg w-4/5">
              <Text className="text-lg font-bold mb-2 text-center">Select Date</Text>
              <DateTimePicker
                value={date}
                mode="date"
                display="spinner"
                onChange={handleDateChange}
                style={{ width: '100%' }}
              />
              <TouchableOpacity
                onPress={() => onClose(date)}
                className="mt-4 bg-blue-500 p-2 rounded"
              >
                <Text className="text-white text-center">
                  Done ({formatDate(date)})
                </Text>
              </TouchableOpacity>
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
        <TouchableOpacity onPress={onPress}>
            <Text className="text-xl text-center">{formatDate(selectedDate)}</Text>
        </TouchableOpacity>
    );
};
