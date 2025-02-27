import React from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";

const BillingBooked = () => {
    return (
        <View className="flex h-screen items-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text="This is the billing booked page" />
        </View>
    );
};

export default BillingBooked;