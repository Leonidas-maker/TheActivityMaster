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
    Animated.timing(animValue, {
      toValue: currentStep,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [currentStep]);

  return (
    <View className="flex-row items-center justify-center my-4 w-full px-4">
      {Array.from({ length: totalSteps }).map((_, index) => {
        // Scale the active step's circle.
        const scale = animValue.interpolate({
          inputRange: [index - 0.5, index, index + 0.5],
          outputRange: [1, 1.2, 1],
          extrapolate: "clamp",
        });

        const circle = (
          <Animated.View
            style={{ transform: [{ scale }] }}
            className={`w-8 h-8 rounded-full flex items-center justify-center ${
              index <= currentStep ? "bg-blue-500" : "bg-gray-300"
            }`}
          >
            <DefaultText text={`${index + 1}`} />
          </Animated.View>
        );

        return (
          <React.Fragment key={index}>
            {index <= currentStep && onStepPress ? (
              <TouchableOpacity onPress={() => onStepPress(index)}>
                {circle}
              </TouchableOpacity>
            ) : (
              circle
            )}
            {index < totalSteps - 1 && (
              <View className="flex-1 h-1 bg-gray-300">
                {index < currentStep ? (
                  // If the step is completed, the connecting line is fully filled.
                  <View className="bg-blue-500 h-full rounded-full" style={{ width: "100%" }} />
                ) : index === currentStep ? (
                  // For the current step, fill the connecting line based on field progress.
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