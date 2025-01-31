import * as SecureStore from "expo-secure-store";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Array der SecureStore Schlüssel direkt im Code definiert
const secureStoreKeys = [
  "uuid",
  "savedPassword",
];

// Function to clear all data from AsyncStorage
const clearAsyncStorage = async () => {
  try {
    await AsyncStorage.clear();
    console.log("AsyncStorage successfully cleared");
  } catch (err) {
    console.error("Error clearing data from AsyncStorage:", err);
  }
};

// Function to clear all data from SecureStore
const clearSecureStorage = async () => {
  try {
    // Promise.all wartet, bis alle Löschvorgänge abgeschlossen sind
    await Promise.all(
      secureStoreKeys.map(async (key) => {
        await SecureStore.deleteItemAsync(key);
      })
    );
    console.log("SecureStore successfully cleared");
  } catch (err) {
    console.error("Error clearing data from SecureStore:", err);
  }
};

// Function to clear both storages
const clearAllStorage = async () => {
  await clearAsyncStorage();
  await clearSecureStorage();
};

export { 
  clearAsyncStorage, 
  clearSecureStorage,
  clearAllStorage 
};