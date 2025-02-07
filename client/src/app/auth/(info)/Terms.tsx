// Terms.tsx
import React, { useEffect, useState } from "react";
import { View, TouchableOpacity, ScrollView } from "react-native";
import Markdown from "react-native-markdown-display";
import { useRouter } from "expo-router";
import { getGerTerms, getEnTerms } from "@/src/services/termsService";
import { useTranslation } from "react-i18next";

const Terms = () => {
    const router = useRouter();
    const { i18n } = useTranslation("auth");
    const [termsText, setTermsText] = useState("");
    const [scrolledToBottom, setScrolledToBottom] = useState(false);

    // Handler for the scroll event to check if the bottom is reached
    const handleScroll = (event: any) => {
        const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;
        // Check if the user has scrolled to within 20 pixels of the bottom
        if (layoutMeasurement.height + contentOffset.y >= contentSize.height - 20) {
            setScrolledToBottom(true);
        }
    };

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
                onScroll={handleScroll}
                scrollEventThrottle={16}
            >
                <Markdown
                    style={{
                        body: { color: "#000", fontSize: 16 },
                    }}
                >
                    {termsText}
                </Markdown>
            </ScrollView>

            <View className="flex-row justify-around items-center bg-white dark:bg-gray-800 py-4 border-t border-gray-200 dark:border-gray-700">
                {/* Decline button */}
                <TouchableOpacity
                    onPress={() => {
                        // Pfusch here, but you get the idea :) (expo issue #26922)
                        router.back();
                        router.push({ pathname: "/auth/SignUp", params: { acceptedTerms: "false" } });
                    }}
                    className="p-4 rounded-md"
                >
                    <Markdown
                        style={{
                            body: { color: "red", fontSize: 18, fontWeight: "bold" },
                        }}
                    >
                        Ablehnen
                    </Markdown>
                </TouchableOpacity>

                {/* Accept button */}
                <TouchableOpacity
                    onPress={() => {
                        if (scrolledToBottom) {
                            // Pfusch here, but you get the idea :) (expo issue #26922)
                            router.back();
                            router.push({ pathname: "/auth/SignUp", params: { acceptedTerms: "true" } });
                        }
                    }}
                    disabled={!scrolledToBottom}
                    className={`p-4 rounded-md ${scrolledToBottom ? "" : "bg-gray-300"}`}
                >
                    <Markdown
                        style={{
                            body: {
                                color: scrolledToBottom ? "green" : "gray",
                                fontSize: 18,
                                fontWeight: "bold",
                            },
                        }}
                    >
                        Akzeptieren
                    </Markdown>
                </TouchableOpacity>
            </View>
        </View>
    );
};

export default Terms;