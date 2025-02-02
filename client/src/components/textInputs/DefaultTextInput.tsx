// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React, { forwardRef, useState, useEffect } from "react";
import {
  TextInput,
  NativeSyntheticEvent,
  TextInputChangeEventData,
  useColorScheme,
} from "react-native";

// ~~~~~~~~~~~ Interfaces imports ~~~~~~~~~ //
import { DefaultTextFieldInputProps } from "../../interfaces/componentInterfaces";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const DefaultTextFieldInput = forwardRef<TextInput, DefaultTextFieldInputProps>(
  (
    {
      autoCapitalize = "sentences",
      autoComplete = "off",
      autoCorrect = true,
      autoFocus = false,
      blurOnSubmit = true,
      defaultValue = "",
      editable = true,
      enterKeyHint = "done",
      keyboardType = "default",
      maxLength = undefined,
      multiline = false,
      onChange,
      onChangeText,
      onFocus = () => {},
      onKeyPress,
      placeholder = "Eingabe",
      secureTextEntry = false,
      selectTextOnFocus = false,
      textAlign = "left",
      value: initialValue = "",
      isOTP = false,
      hasError = false,
    },
    ref,
  ) => {
    // ====================================================== //
    // ======================= States ======================= //
    // ====================================================== //
    const [value, setValue] = useState(initialValue);
    const [isLight, setIsLight] = useState(false);

    // ~~~~~~~~~~~ Use color scheme ~~~~~~~~~~ //
    const colorScheme = useColorScheme();
    useEffect(() => {
      setIsLight(colorScheme === "light");
    }, [colorScheme]);

    const placeholderTextColor = isLight ? "#000000" : "#FFFFFF";

    // ====================================================== //
    // ====================== Functions ===================== //
    // ====================================================== //
    const handleOnChange = (
      e: NativeSyntheticEvent<TextInputChangeEventData>,
    ) => {
      const newText = e.nativeEvent.text;
      setValue(newText);
      if (onChange) onChange(e);
    };

    const handleChangeText = (text: string) => {
      setValue(text);
      if (onChangeText) onChangeText(text);
    };

    // ====================================================== //
    // ===================== Styling ======================== //
    // ====================================================== //
    const baseClasses =
      "bg-light_secondary dark:bg-dark_secondary text-black dark:text-white border-2 rounded-xl opacity-75 focus:opacity-100 m-2";
    const errorClasses = hasError
      ? " border-red-500 dark:border-red-500 focus:border-red-600 dark:focus:border-red-600"
      : " border-light_secondary dark:border-dark_secondary focus:border-light_action dark:focus:border-dark_action";

    let inputClassName = "";
    if (isOTP) {
      inputClassName = `${baseClasses} text-center${errorClasses}`;
    } else {
      inputClassName = `${baseClasses} w-3/4 h-10 p-2${errorClasses}`;
    }

    // ====================================================== //
    // ================== Return component ================== //
    // ====================================================== //
    return (
      <TextInput
        style={isOTP ? { width: 40, height: 40 } : {}}
        className={inputClassName}
        ref={ref}
        autoCapitalize={autoCapitalize}
        autoComplete={autoComplete}
        autoCorrect={autoCorrect}
        autoFocus={autoFocus}
        blurOnSubmit={blurOnSubmit}
        defaultValue={defaultValue}
        editable={editable}
        enterKeyHint={enterKeyHint}
        keyboardType={keyboardType}
        maxLength={maxLength}
        multiline={multiline}
        onChange={handleOnChange}
        onChangeText={handleChangeText}
        onFocus={onFocus}
        onKeyPress={onKeyPress}
        placeholder={placeholder}
        placeholderTextColor={placeholderTextColor}
        secureTextEntry={secureTextEntry}
        selectTextOnFocus={selectTextOnFocus}
        textAlign={textAlign}
        value={value}
      />
    );
  },
);

export default DefaultTextFieldInput;
