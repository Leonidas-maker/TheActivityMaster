// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import {
  ViewStyle,
  TextInputProps,
  TextInputKeyPressEventData,
  TextInputChangeEventData,
  NativeSyntheticEvent,
  ImageSourcePropType,
} from "react-native";
import { SharedValue } from "react-native-reanimated";

interface TextProps {
  text: string;
}

interface RadioOptionProps {
  label: string;
  onPress: () => void;
  checked: boolean;
  radioColor: string;
}

interface NavigatorProps {
  title: string;
  onPressFunctions: (() => void)[];
  texts: string[];
  iconNames: string[];
  isExternalLink?: boolean[];
}

interface OptionSelectorProps {
  title: string;
  onPressFunctions: (() => void)[];
  texts: string[];
  iconNames: string[];
  checked: boolean[];
  isEmoji?: boolean;
}

interface DefaultButtonProps {
  text?: string;
  onPress?: () => void;
  onPressIn?: () => void;
  onPressOut?: () => void;
  onLongPress?: () => void;
  disabled?: boolean;
  delayLongPress?: number;
  unstable_pressDelay?: number;
  isCancel?: boolean;
}

interface DefaultTextFieldInputProps {
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  autoComplete?:
    | "additional-name"
    | "address-line1"
    | "address-line2"
    | "birthdate-day"
    | "birthdate-full"
    | "birthdate-month"
    | "birthdate-year"
    | "cc-csc"
    | "cc-exp"
    | "cc-exp-day"
    | "cc-exp-month"
    | "cc-exp-year"
    | "cc-number"
    | "country"
    | "current-password"
    | "email"
    | "family-name"
    | "given-name"
    | "honorific-prefix"
    | "honorific-suffix"
    | "name"
    | "new-password"
    | "off"
    | "one-time-code"
    | "postal-code"
    | "street-address"
    | "tel"
    | "username"
    | "cc-family-name"
    | "cc-given-name"
    | "cc-middle-name"
    | "cc-name"
    | "cc-type"
    | "nickname"
    | "organization"
    | "organization-title"
    | "url"
    | "gender"
    | "name-family"
    | "name-given"
    | "name-middle"
    | "name-middle-initial"
    | "name-prefix"
    | "name-suffix"
    | "password"
    | "password-new"
    | "postal-address"
    | "postal-address-country"
    | "postal-address-extended"
    | "postal-address-extended-postal-code"
    | "postal-address-locality"
    | "postal-address-region"
    | "sms-otp"
    | "tel-country-code"
    | "tel-device"
    | "tel-national"
    | "username-new";
  autoCorrect?: boolean;
  autoFocus?: boolean;
  blurOnSubmit?: boolean;
  defaultValue?: string;
  editable?: boolean;
  enterKeyHint?: "enter" | "done" | "next" | "previous" | "search" | "send";
  keyboardType?: TextInputProps["keyboardType"];
  maxLength?: number;
  multiline?: boolean;
  onChange?: (e: NativeSyntheticEvent<TextInputChangeEventData>) => void;
  onChangeText?: (text: string) => void;
  onFocus?: () => void;
  onKeyPress?: (e: NativeSyntheticEvent<TextInputKeyPressEventData>) => void;
  placeholder?: string;
  secureTextEntry?: boolean;
  selectTextOnFocus?: boolean;
  textAlign?: "left" | "center" | "right";
  value?: string;
  isOTP?: boolean;
  hasError?: boolean;
}

interface OptionSwitchProps {
  title: string;
  texts: string[];
  iconNames: string[];
  onValueChanges: ((value: boolean) => void)[];
  values: boolean[];
}

interface DropdownProps {
  setSelected: (value: string) => void;
  values: {
    key: string;
    value: string;
    disabled?: boolean;
  }[];
  placeholder?: string;
  search?: boolean;
  boxStyles?: ViewStyle;
  dropdownStyles?: ViewStyle;
  dropdownTextStyles?: ViewStyle;
  inputStyles?: ViewStyle;
  notFound?: string;
  save?: "value" | "key" | undefined;
  defaultOption?: { key: any; value: any };
}

interface WeekSelectProps {
  onBackPress: () => void;
  onForwardPress: () => void;
  onTodayPress?: () => void;
  startDate?: Date;
  endDate?: Date;
  currentDate?: Date;
  mode: string;
}

export {
  TextProps,
  RadioOptionProps,
  NavigatorProps,
  DefaultButtonProps,
  OptionSelectorProps,
  DefaultTextFieldInputProps,
  OptionSwitchProps,
  DropdownProps,
  WeekSelectProps,
};
