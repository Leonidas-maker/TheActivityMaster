// ~~~~~~~~~~~~~~~ Imports ~~~~~~~~~~~~~~~ //
import React from "react";
import { View, ScrollView, Linking } from "react-native";

// ~~~~~~~~ Own components imports ~~~~~~~ //
import DefaultText from "@/src/components/textFields/DefaultText";
import Heading from "@/src/components/textFields/Heading";
import TextButton from "@/src/components/buttons/TextButton";
import Subheading from "@/src/components/textFields/Subheading";

// ====================================================== //
// ====================== Component ===================== //
// ====================================================== //
const Imprint = () => {
    // ====================================================== //
    // =================== Press handlers =================== //
    // ====================================================== //
    const handleMailPress = () => {
        Linking.openURL("mailto:contact@theactivitymaster.de");
    };

    // ====================================================== //
    // ================== Return component ================== //
    // ====================================================== //
    return (
        <ScrollView className="h-screen bg-light_primary dark:bg-dark_primary">
            <View className="px-5 py-5">
                <View className="mb-5">
                    <Heading text="Kontaktinformationen" />
                    <Subheading text="Die App ist im Rahmen einer Studienarbeit der DHBW Mannheim enstanden." />
                </View>
                <View className="flex-1 mx-5">
                    <View className="mb-5">
                        <DefaultText text="Unter anderem entwickelt von:" />
                    </View>
                    <View className="mb-3">
                        <DefaultText text="Andreas Schütz," />
                    </View>
                    <View className="mb-3">
                        <DefaultText text="Leon Sylvester" />
                    </View>
                    <View className="mb-3 flex-row">
                        <DefaultText text="E-Mail: " />
                        <TextButton
                            text="contact@theactivitymaster.de"
                            onPress={handleMailPress}
                        />
                    </View>
                </View>
            </View>
        </ScrollView>
    );
};

export default Imprint;
