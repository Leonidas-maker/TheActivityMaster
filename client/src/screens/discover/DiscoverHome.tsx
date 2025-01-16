import React from "react";
import { View } from "react-native";
import DefaultText from "../../components/textFields/DefaultText";

const DiscoverHome: React.FC = () => {
    return (
        <View className={"flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary"}>
            <DefaultText text="Welcome to Discover" />
        </View>
    );
};

export default DiscoverHome;