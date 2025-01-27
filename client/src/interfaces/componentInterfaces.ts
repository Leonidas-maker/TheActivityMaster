import OptionSelector from '../components/optionSelector/OptionSelector';
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

export { TextProps, RadioOptionProps, NavigatorProps, DefaultButtonProps, OptionSelectorProps };
