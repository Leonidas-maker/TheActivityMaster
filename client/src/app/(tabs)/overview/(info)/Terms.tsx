// Terms.tsx
import React, { useEffect, useState } from "react";
import { View, TouchableOpacity, ScrollView, Text } from "react-native";
import Markdown from "react-native-markdown-display";
import { useRouter } from "expo-router";
import { getGerTerms, getEnTerms } from "@/src/services/static/termsService";
import { useTranslation } from "react-i18next"
import { useColorScheme } from "nativewind";

const Terms = () => {
    const router = useRouter();
    const { i18n, t } = useTranslation("auth");
    const [termsText, setTermsText] = useState("");
    const [isLight, setIsLight] = useState(false);

    const { colorScheme } = useColorScheme();

    useEffect(() => {
        if (colorScheme === "light") {
            setIsLight(true);
        } else {
            setIsLight(false);
        }
    }, [colorScheme]);

    const textColor = isLight ? "#000" : "#FFFFFF";

    const getTerms = async () => {
        const language = i18n.language;
        if (language === "de") {
            setTermsText(await getGerTerms());
        } else {
            setTermsText(await getEnTerms());
        }
    }

    useEffect(() => {
        getTerms();
    }, []);

    return (
        <View className="flex-1 bg-light_primary dark:bg-dark_primary justify-between">
            <ScrollView
                className="flex-1 px-4"
                contentContainerStyle={{ paddingVertical: 20 }}
                showsVerticalScrollIndicator={false}
                scrollEventThrottle={16}
            >
                <Markdown
                    style={{
                        body: { color: textColor, fontSize: 16 },
                    }}
                >
                    {termsText}
                </Markdown>
            </ScrollView>
        </View>
    );
};

export default Terms;