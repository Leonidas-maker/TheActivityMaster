// ProgressBar.tsx
import React, { useEffect, useRef } from "react";
import { View, TouchableOpacity, Animated } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import PartialFillWrapper from "./PartialFillWrapper";

interface StepProgressBarProps {
  currentStep: number;
  totalSteps: number;
  fieldProgress?: number; // Field completion progress for the current step (0–1)
  onStepPress?: (step: number) => void;
}

const StepProgressBar: React.FC<StepProgressBarProps> = ({
  currentStep,
  totalSteps,
  fieldProgress = 0,
  onStepPress,
}) => {
  // Animated value for scaling the active circle.
  const animValue = useRef(new Animated.Value(currentStep)).current;
  useEffect(() => {
    if (currentStep === 0) {
      // For the first step, disable the animation.
      animValue.setValue(currentStep);
    } else {
      Animated.timing(animValue, {
        toValue: currentStep,
        duration: 300,
        useNativeDriver: false,
      }).start();
    }
  }, [currentStep]);

  return (
    <View className="flex-row items-center justify-center my-4 w-full px-4 relative">
      {Array.from({ length: totalSteps }).map((_, index) => {
        // Interpolate the scale so that the active circle "pops"
        const scale = animValue.interpolate({
          inputRange: [index - 0.5, index, index + 0.5],
          outputRange: [1, 1.2, 1],
          extrapolate: "clamp",
        });

        // The circle element with a high z-index so it sits above the connecting line.
        const circle = (
          <Animated.View
            style={{
              transform: [{ scale }],
              zIndex: 10, // Ensure the circle is on top
              position: "relative", // Must be positioned for zIndex to take effect
            }}
            className={`w-8 h-8 rounded-full flex items-center justify-center ${
              index <= currentStep ? "bg-green-400 dark:bg-green-600" : "bg-gray-300"
            }`}
          >
            <DefaultText text={`${index + 1}`} />
          </Animated.View>
        );

        return (
          <React.Fragment key={index}>
            {index <= currentStep && onStepPress ? (
              // Make the circle clickable if this step is accessible.
              <TouchableOpacity onPress={() => onStepPress(index)}>
                {circle}
              </TouchableOpacity>
            ) : (
              circle
            )}
            {index < totalSteps - 1 && (
              // The connecting line between steps.
              <View
                style={{
                  position: "relative",
                  zIndex: -1, // Place the connecting line behind the circle
                }}
                className="flex-1 h-1 bg-gray-300"
              >
                {index < currentStep ? (
                  // For already completed steps, the connecting line is fully filled.
                  <View className="bg-green-400 dark:bg-green-600 h-full rounded-full" style={{ width: "100%" }} />
                ) : index === currentStep ? (
                  // For the current step, fill gradually based on field progress.
                  <PartialFillWrapper fieldProgress={fieldProgress} />
                ) : null}
              </View>
            )}
          </React.Fragment>
        );
      })}
    </View>
  );
};

export default StepProgressBar;
