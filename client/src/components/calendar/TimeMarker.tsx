// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { useState, useEffect } from "react";
import { View } from "react-native";
import "nativewind";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import {
  calculateMarkerPosition,
  calculateDayHeight,
} from "./CalendarCalculations";

// ~~~~~~~~~~ Interfaces imports ~~~~~~~~~ //
import { TimeMarkerProps } from "../../interfaces/calendarInterfaces";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const TimeMarker: React.FC<TimeMarkerProps> = ({
  hoursContainerHeight,
  containerHeight,
  calendar,
}) => {
  // ====================================================== //
  // ======================= States ======================= //
  // ====================================================== //
  const [showTimeMarker, setShowTimeMarker] = useState(true);
  // State for storing the current marker position
  const [markerPosition, setMarkerPosition] = useState(
    calculateMarkerPosition({
      startHour: calendar.startHour,
      endHour: calendar.endHour,
      hoursContainerHeight: hoursContainerHeight,
      containerHeight: containerHeight,
    })
  );

  // Calculate the day height
  const dayHeight = calculateDayHeight(containerHeight, hoursContainerHeight);

  // ====================================================== //
  // ========== Update marker position every minute ====== //
  // ====================================================== //
  useEffect(() => {
    // Function to update the marker position
    const updateMarkerPosition = () => {
      const newPosition = calculateMarkerPosition({
        startHour: calendar.startHour,
        endHour: calendar.endHour,
        hoursContainerHeight: hoursContainerHeight,
        containerHeight: containerHeight,
      });
      setMarkerPosition(newPosition);
    };

    // Update immediately when component mounts
    updateMarkerPosition();

    // Set interval to update every minute (60000 milliseconds)
    const intervalId = setInterval(() => {
      updateMarkerPosition();
    }, 60000);

    // Clear interval on component unmount
    return () => clearInterval(intervalId);
  }, [calendar, hoursContainerHeight, containerHeight]);

  // ====================================================== //
  // ========== Toggle visibility of the Time Marker ====== //
  // ====================================================== //
  useEffect(() => {
    if (markerPosition < dayHeight) {
      setShowTimeMarker(false);
    } else {
      setShowTimeMarker(true);
    }
  }, [markerPosition, dayHeight]);

  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <View className="absolute w-full">
      {showTimeMarker && (
        <View
          className="bg-light_action dark:bg-dark_action rounded-lg shadow-sm"
          style={{
            position: "absolute",
            top: markerPosition,
            width: "100%",
            height: 2,
          }}
        ></View>
      )}
    </View>
  );
};

export default TimeMarker;
