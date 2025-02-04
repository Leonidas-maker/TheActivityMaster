// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { useState, useEffect } from "react";
import { View } from "react-native";
import "nativewind";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import {
  calculateMarkerPositionFilled,
  calculateDayHeight,
} from "./CalendarCalculations";

// ~~~~~~~~~~ Interfaces imports ~~~~~~~~~ //
import { PastMarkerProps } from "../../interfaces/calendarInterfaces";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const PastMarker: React.FC<PastMarkerProps> = ({
  hoursContainerHeight,
  containerHeight,
  calendar,
  isToday,
}) => {
  // ====================================================== //
  // =============== PastMarker calculations ============== //
  // ====================================================== //
  // Calculate the day height
  const dayHeight = calculateDayHeight(containerHeight, hoursContainerHeight);
  // Sets the Past Height as the Hours Container Height
  const pastHeight = hoursContainerHeight;
  
  // State for storing the current markerPositionFilled
  const [markerPositionFilled, setMarkerPositionFilled] = useState(
    calculateMarkerPositionFilled({
      startHour: calendar.startHour,
      endHour: calendar.endHour,
      hoursContainerHeight: hoursContainerHeight,
      containerHeight: containerHeight,
    })
  );

  // ====================================================== //
  // ===== Update markerPositionFilled every minute ====== //
  // ====================================================== //
  useEffect(() => {
    // Function to update the markerPositionFilled
    const updateMarkerPositionFilled = () => {
      const newPosition = calculateMarkerPositionFilled({
        startHour: calendar.startHour,
        endHour: calendar.endHour,
        hoursContainerHeight: hoursContainerHeight,
        containerHeight: containerHeight,
      });
      setMarkerPositionFilled(newPosition);
    };

    // Update immediately when the component mounts
    updateMarkerPositionFilled();

    // Set interval to update every minute (60000 milliseconds)
    const intervalId = setInterval(() => {
      updateMarkerPositionFilled();
    }, 60000);

    // Clear interval on component unmount
    return () => clearInterval(intervalId);
  }, [calendar, hoursContainerHeight, containerHeight]);

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <View className="absolute w-full">
      {!isToday && (
        <View
          className="bg-gray-900 dark:bg-gray-400 opacity-30"
          style={{
            position: "absolute",
            top: dayHeight,
            width: "100%",
            height: pastHeight,
          }}
        ></View>
      )}
      {isToday && (
        <View
          className="bg-gray-900 dark:bg-gray-400 opacity-30"
          style={{
            position: "absolute",
            top: dayHeight,
            width: "100%",
            height: markerPositionFilled,
          }}
        ></View>
      )}
    </View>
  );
};

export default PastMarker;