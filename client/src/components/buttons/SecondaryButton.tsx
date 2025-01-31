// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { Pressable, Text } from "react-native";

// ~~~~~~~~~~ Interfaces imports ~~~~~~~~~ //
import { DefaultButtonProps } from "../../interfaces/componentInterfaces";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const SecondaryButton: React.FC<DefaultButtonProps> = ({
  text = "Drück mich",
  onPress,
  onPressIn,
  onPressOut,
  onLongPress,
  disabled = false,
  delayLongPress = 500,
  unstable_pressDelay = 1,
  isCancel = false,
}) => {
  // ====================================================== //
  // ================== Return component ================== //
  // ====================================================== //
  return (
    <Pressable
      className={
        isCancel
          ? "bg-neutral-300 w-3/4 h-10 rounded-xl justify-center items-center active:bg-neutral-600"
          : "bg-neutral-700 dark:bg-neutral-300 w-3/4 h-10 rounded-xl justify-center items-center active:bg-neutral-900 dark:active:bg-neutral-400 m-2"
      }
      onPress={onPress}
      onPressIn={onPressIn}
      onPressOut={onPressOut}
      onLongPress={onLongPress}
      disabled={disabled}
      delayLongPress={delayLongPress}
      unstable_pressDelay={unstable_pressDelay}
    >
      <Text className="text-white dark:text-black">{text}</Text>
    </Pressable>
  );
};

export default SecondaryButton;