import React, { useState, useEffect } from "react";
import { View } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { getUserData } from "@/src/services/user/userService";

const SettingsUser: React.FC = () => {
    //TODO: Implement the user settings page
    //! This is only for testing purposes
    // State to store the response as a string
    const [response, setResponse] = useState<string>("");

    useEffect(() => {
        // Fetch user data and update the state with a JSON string
        getUserData().then((data) => {
            // Convert the object to a formatted JSON string
            setResponse(JSON.stringify(data, null, 2));
        });
    }, []);

    return (
        <View className="flex h-screen items-center justify-center bg-light_primary dark:bg-dark_primary">
            <DefaultText text={response} />
        </View>
    );
};

export default SettingsUser;
