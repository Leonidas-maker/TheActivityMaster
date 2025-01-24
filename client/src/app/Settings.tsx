import React, { useState, useEffect } from "react";
import { useColorScheme } from "nativewind";
import { useTheme  } from "@/src/provider/ThemeProvider";
import { View, ScrollView } from "react-native";
import Subheading from "@/src/components/textFields/Subheading";
import RadioOption from "@/src/components/radioOption/RadioOption";

const Settings: React.FC = () => {
  const [isLight, setIsLight] = useState(false);

  const { theme, setTheme } = useTheme();

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
            onPress={() => setTheme("light")}
            checked={theme === "light"}
            radioColor={radioColor}
          />
          <RadioOption
            label="Dark Mode"
            onPress={() => setTheme("dark")}
            checked={theme === "dark"}
            radioColor={radioColor}
          />
          <RadioOption
            label="System Mode"
            onPress={() => setTheme("system")}
            checked={theme === "system"}
            radioColor={radioColor}
          />
        </View>
      </ScrollView>
  );
};

export default Settings;
