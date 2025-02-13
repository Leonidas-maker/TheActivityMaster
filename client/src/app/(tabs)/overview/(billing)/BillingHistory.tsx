import React from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";

const BillingHistory = () => {
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the billing history page" />
        </View>
    );
};

export default BillingHistory;