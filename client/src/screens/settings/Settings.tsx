import React, {
    useState,
    useEffect
} from "react";
import { useColorScheme } from "nativewind";
import { useTheme } from "../../provider/ThemeProvider";
import { View, ScrollView } from "react-native";
import Subheading from "../../components/textFields/Subheading";
import RadioOption from "../../components/radioOption/RadioOption";

type SchemeType = "light" | "dark" | "system";

const Settings: React.FC = () => {

    const [isLight, setIsLight] = useState(false);

    const { theme, setTheme } = useTheme();

    // Set the scheme
    const setScheme = (scheme: SchemeType) => {
        setTheme(scheme);
    };

    // ~~~~~~~~~~~~~~ Use Color Scheme ~~~~~~~~~~~~~~ //
    const { colorScheme, setColorScheme } = useColorScheme();

    // Set the color scheme
    useEffect(() => {
        setColorScheme(theme);
    }, [theme, setColorScheme]);

    // Set if the theme is light or dark
    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    // Color based on the theme
    const radioColor = isLight ? "#171717" : "#E0E2DB";

    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="p-4">
                <Subheading text="Design auswählen" />
                <RadioOption
                    label="Light Mode"
                    onPress={() => setScheme("light")}
                    checked={theme === "light"}
                    radioColor={radioColor}
                />
                <RadioOption
                    label="Dark Mode"
                    onPress={() => setScheme("dark")}
                    checked={theme === "dark"}
                    radioColor={radioColor}
                />
                <RadioOption
                    label="System Mode"
                    onPress={() => setScheme("system")}
                    checked={theme === "system"}
                    radioColor={radioColor}
                />

            </View>
        </ScrollView>
    );
};

export default Settings;