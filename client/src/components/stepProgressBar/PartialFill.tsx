import React, { useEffect, useRef } from "react";
import { Animated } from "react-native";

interface PartialFillProps {
  fieldProgress: number; // Value between 0 and 1
  containerWidth: number;
}

const PartialFill: React.FC<PartialFillProps> = ({ fieldProgress, containerWidth }) => {
  const fillWidth = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Animate the fill width based on the fieldProgress value.
    Animated.timing(fillWidth, {
      toValue: fieldProgress * containerWidth,
      duration: 300,
      useNativeDriver: false, // Width cannot be animated with the native driver.
    }).start();
  }, [fieldProgress, containerWidth]);

  return (
    <Animated.View
      style={{ width: fillWidth }}
      className="bg-green-400 dark:bg-green-600 h-full rounded-full -z-50"
    />
  );
};

export default PartialFill;
