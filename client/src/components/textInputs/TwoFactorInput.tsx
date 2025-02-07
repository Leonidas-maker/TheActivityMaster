import React, { useState, useRef } from 'react';
import {
  View,
  TextInput,
  NativeSyntheticEvent,
  TextInputKeyPressEventData,
} from 'react-native';

interface TwoFactorInputProps {
  codeLength?: number; // Number of digits in the 2FA code (default is 6)
  /**
   * Called when all fields are filled with digits.
   */
  onComplete?: (code: string) => void;
  /**
   * Called whenever the code changes.
   *   - code: the full code as a string (concatenated digits)
   *   - isComplete: true if every field is filled, false otherwise
   */
  onCodeChange?: (code: string, isComplete: boolean) => void;
}

const TwoFactorInput: React.FC<TwoFactorInputProps> = ({
  codeLength = 6,
  onComplete,
  onCodeChange,
}) => {
  // Store each digit in an array of strings.
  const [code, setCode] = useState<string[]>(Array(codeLength).fill(''));
  // Refs for each TextInput to manage focus.
  const inputRefs = useRef<Array<TextInput | null>>(new Array(codeLength).fill(null));

  /**
   * Helper function to update the code state and trigger callbacks.
   * @param newCode - The updated array of digits.
   */
  const updateCode = (newCode: string[]) => {
    setCode(newCode);
    const codeString = newCode.join('');
    const isComplete = newCode.every((digit) => digit !== '');
    if (onCodeChange) {
      onCodeChange(codeString, isComplete);
    }
    if (isComplete && onComplete) {
      onComplete(codeString);
    }
  };

  /**
   * Handles changes to a specific input field.
   * - Supports pasting multiple digits.
   * - Auto-advances to the next field.
   * - If the last digit is entered, the last field loses focus.
   */
  const handleChange = (index: number, text: string) => {
    // If the user pastes multiple characters, fill fields sequentially.
    if (text.length > 1) {
      const newCode = [...code];
      let currentIndex = index;
      for (let i = 0; i < text.length && currentIndex < codeLength; i++) {
        const char = text[i];
        if (/^\d$/.test(char)) {
          newCode[currentIndex] = char;
          currentIndex++;
        }
      }
      updateCode(newCode);
      // Focus the next field if available; if not, blur the last one.
      if (currentIndex < codeLength) {
        inputRefs.current[currentIndex]?.focus();
      } else {
        inputRefs.current[codeLength - 1]?.blur();
      }
      return;
    }

    // For single-character input, allow only digits.
    const newValue = text.slice(-1);
    if (newValue && !/^\d$/.test(newValue)) return;

    const newCode = [...code];
    newCode[index] = newValue;
    updateCode(newCode);

    // Auto-advance to the next field if it's not the last.
    if (newValue !== '' && index < codeLength - 1) {
      inputRefs.current[index + 1]?.focus();
    }
    // If the last field was updated with a digit, remove focus.
    if (index === codeLength - 1 && newValue !== '') {
      inputRefs.current[index]?.blur();
    }
  };

  /**
   * Handles key press events.
   * When backspace is pressed:
   * - If the current field is empty, delete the digit in the previous field and focus it.
   * - Otherwise, simply clear the current field.
   */
  const handleKeyPress = (
    e: NativeSyntheticEvent<TextInputKeyPressEventData>,
    index: number
  ) => {
    if (e.nativeEvent.key === 'Backspace') {
      const newCode = [...code];
      if (newCode[index] === '') {
        if (index > 0) {
          newCode[index - 1] = '';
          updateCode(newCode);
          inputRefs.current[index - 1]?.focus();
        }
      } else {
        newCode[index] = '';
        updateCode(newCode);
      }
    }
  };

  return (
    <View className="flex-row justify-center">
      {code.map((digit, index) => (
        <TextInput
          key={index}
          ref={(ref) => (inputRefs.current[index] = ref)}
          value={digit}
          onChangeText={(text) => handleChange(index, text)}
          onKeyPress={(e) => handleKeyPress(e, index)}
          keyboardType="number-pad"
          maxLength={1}
          autoFocus={index === 0}
          className="w-12 h-12 text-center bg-light_secondary dark:bg-dark_secondary text-black dark:text-white border-2 rounded-xl opacity-75 focus:opacity-100 m-2 border-light_secondary dark:border-dark_secondary focus:border-light_action dark:focus:border-dark_action"
        />
      ))}
    </View>
  );
};

export default TwoFactorInput;
