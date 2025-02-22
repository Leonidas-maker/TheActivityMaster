import React, { useEffect, useState } from "react";
import { View, Image, Text, ScrollView } from "react-native";
import DefaultText from "@/src/components/textFields/DefaultText";
import { useTranslation } from "react-i18next";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getVerification, getVerificationImage } from "@/src/services/verificiation/identityService";

const AdminIdentityApprove = () => {
    const { t } = useTranslation("admin");
    const router = useRouter();

    const { verification_id } = useLocalSearchParams();

    // State for storing verification details and images
    const [verificationDetails, setVerificationDetails] = useState(null);
    const [frontImage, setFrontImage] = useState(null);
    const [backImage, setBackImage] = useState(null);
    const [selfieImage, setSelfieImage] = useState(null);

    useEffect(() => {
        const fetchVerification = async () => {
            try {
                // Ensure we have a valid id from the URL parameters
                const id = Array.isArray(verification_id) ? verification_id[0] : verification_id;

                // Fetch verification details only once
                const verification = await getVerification(id);
                console.log("Verification:", verification);
                setVerificationDetails(verification);

                // Concurrently fetch the images using correct indexes:
                // 0 for front image, 1 for back image, 2 for selfie image.
                const [frontImg, backImg, selfieImg] = await Promise.all([
                    getVerificationImage(id, 0),
                    getVerificationImage(id, 1),
                    getVerificationImage(id, 2)
                ]);
                console.log("Front Image:", frontImg);
                console.log("Back Image:", backImg);
                console.log("Selfie Image:", selfieImg);

                // Set state based on whether an image was returned or not
                setFrontImage(frontImg || null);
                setBackImage(backImg || null);
                setSelfieImage(selfieImg || null);
            } catch (error) {
                console.error("Failed to fetch verification:", error);
            }
        };

        fetchVerification();
    }, [verification_id]);

    return (
        <ScrollView contentContainerStyle={{ flexGrow: 1 }} className="flex bg-light_primary dark:bg-dark_primary p-4">
            <DefaultText text={t("test_text")} />

            {/* Display verification details */}
            <View className="my-4">
                <DefaultText text="Verification Details:" />
                {verificationDetails ? (
                    <DefaultText text={JSON.stringify(verificationDetails, null, 2)} />
                ) : (
                    <DefaultText text="No verification details available" />
                )}
            </View>

            {/* Display images with conditional rendering */}
            <View className="my-2">
                {frontImage ? (
                    <Image source={{ uri: frontImage }} style={{ width: 200, height: 200 }} />
                ) : (
                    <DefaultText text="Front image not available" />
                )}
            </View>
            <View className="my-2">
                {backImage ? (
                    <Image source={{ uri: backImage }} style={{ width: 200, height: 200 }} />
                ) : (
                    <DefaultText text="Back image not available" />
                )}
            </View>
            <View className="my-2">
                {selfieImage ? (
                    <Image source={{ uri: selfieImage }} style={{ width: 200, height: 200 }} />
                ) : (
                    <DefaultText text="Selfie image not available" />
                )}
            </View>
        </ScrollView>
    );
};

export default AdminIdentityApprove;
