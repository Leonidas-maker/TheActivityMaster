import React, { useEffect, useState } from "react";
import { Image } from "expo-image";
import { ActivityIndicator, View, TouchableOpacity, Modal, StyleSheet } from "react-native";
import { BASE_URL } from "@/src/services/api";
import { secureLoadData } from "@/src/services/secureStorageService";
import generateFingerprint from "@/src/fingerprint/Fingerprint";

interface VerificationImageProps {
  verificationId: string;
  index: number;
}

const VerificationImage = ({ verificationId, index }: VerificationImageProps) => {
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  // State for modal visibility
  const [modalVisible, setModalVisible] = useState<boolean>(false);

  useEffect(() => {
    const fetchVerification = async () => {
      try {
        const fingerprint = await generateFingerprint();
        const access_token = await secureLoadData("access_token");
        setAccessToken(access_token);
        setApplicationId(fingerprint);
      } catch (error) {
        console.error("Failed to fetch verification:", error);
      }
    };

    fetchVerification();
  }, [verificationId]);

  // Construct image URI
  const imageUri = `${BASE_URL}/verification/identity/get/${verificationId}/image?index=${index}`;

  return (
    <>
      <TouchableOpacity onPress={() => setModalVisible(true)}>
        <View style={styles.imageContainer}>
          {/* Display spinner while image loads */}
          {loading && (
            <View style={styles.loadingOverlay}>
              <ActivityIndicator size="large" color="#000" />
            </View>
          )}
          <Image
            style={styles.image}
            contentFit="cover"
            source={{
              uri: imageUri,
              headers: {
                Authorization: `Bearer ${accessToken}`,
                "application-id": `${applicationId}`,
              },
            }}
            onLoadStart={() => setLoading(true)}
            onLoadEnd={() => setLoading(false)}
          />
        </View>
      </TouchableOpacity>

      {/* Modal for full screen image */}
      <Modal visible={modalVisible} transparent={true} onRequestClose={() => setModalVisible(false)}>
        <TouchableOpacity style={styles.modalBackground} onPress={() => setModalVisible(false)}>
          <Image
            style={styles.fullImage}
            contentFit="contain"
            source={{
              uri: imageUri,
              headers: {
                Authorization: `Bearer ${accessToken}`,
                "application-id": `${applicationId}`,
              },
            }}
          />
        </TouchableOpacity>
      </Modal>
    </>
  );
};

const styles = StyleSheet.create({
  imageContainer: {
    width: "100%",
    height: 200,
    position: "relative",
  },
  image: {
    width: "100%",
    height: 200,
  },
  loadingOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.5)",
  },
  modalBackground: {
    flex: 1,
    backgroundColor: "black",
    justifyContent: "center",
    alignItems: "center",
  },
  fullImage: {
    width: "100%",
    height: "100%",
  },
});

export default VerificationImage;
