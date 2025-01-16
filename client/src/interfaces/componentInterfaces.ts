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
  

export { TextProps, RadioOptionProps, NavigatorProps };