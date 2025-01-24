import * as Device from 'expo-device';
import * as Constants from 'expo-constants';
import { getInstallationTimeAsync } from 'expo-application';
import { Dimensions, PixelRatio } from 'react-native';
import * as Crypto from 'expo-crypto';
import { secureSaveData, secureLoadData } from '../services/secureStorageService';

// Normalize values: if null, return "0"
const normalizeValue = (value: any) => (value === null ? "0" : value);

// Extract the major version from a version string (e.g., "18.1.2" -> "18")
const getMajorVersion = (version: any) => {
    if (!version || typeof version !== "string") return "0"; // Fallback for invalid or null values
    const [major] = version.split("."); // Split version by "." and take the first part
    return major || "0"; // Ensure at least "0" is returned if major is undefined
};

const getOrCreateUUID = async () => {
    let uuid = await secureLoadData('uuid'); // Load UUID from secure storage
    if (!uuid) {
        uuid = await Crypto.randomUUID(); // Generate new UUID if not found
        await secureSaveData('uuid', uuid); // Save the new UUID in secure storage
    }
    return uuid; // Return the UUID
};

const generateFingerprint = async () => {
    const uuid = await getOrCreateUUID(); // Ensure UUID is available

    const deviceName = normalizeValue(Device.deviceName);
    const deviceType = normalizeValue(Device.deviceType);
    const deviceYearClass = normalizeValue(Device.deviceYearClass);
    const osName = normalizeValue(Device.osName);
    const osVersion = getMajorVersion(Device.osVersion); // Extract major version
    const manufacturer = normalizeValue(Device.manufacturer);
    const brand = normalizeValue(Device.brand);
    const modelId = normalizeValue(Device.modelId);
    const designName = normalizeValue(Device.designName);
    const modelName = normalizeValue(Device.modelName);
    const totalMemory = normalizeValue(Device.totalMemory);
    const supportedCpuArchitectures = normalizeValue(Device.supportedCpuArchitectures);
    const productName = normalizeValue(Device.productName);
    const platformApiLevel = normalizeValue(Device.platformApiLevel);
    const osBuildFingerprint = normalizeValue(Device.osBuildFingerprint);
    const isDevice = normalizeValue(Device.isDevice);

    const debugMode = normalizeValue(Constants.default.debugMode);
    const statusBarHeight = normalizeValue(Constants.default.statusBarHeight);
    const systemFonts = normalizeValue(Constants.default.systemFonts);

    const { width, height } = Dimensions.get('window');
    const pixelRatio = PixelRatio.get();

    const installationTime = await getInstallationTimeAsync();

    // Combine all data into a single string
    const rawData = [
        deviceName,
        deviceType,
        deviceYearClass,
        osName,
        osVersion,
        manufacturer,
        brand,
        modelId,
        designName,
        modelName,
        totalMemory,
        supportedCpuArchitectures,
        installationTime,
        productName,
        platformApiLevel,
        osBuildFingerprint,
        isDevice,
        debugMode,
        statusBarHeight,
        systemFonts,
        width,
        height,
        pixelRatio,
        uuid, // Include the UUID
    ].join(""); // Join all values without a separator

    // Hash the combined data using SHA-512 with expo-crypto
    const hashedData = await Crypto.digestStringAsync(
        Crypto.CryptoDigestAlgorithm.SHA512,
        rawData
    );

    console.log('Raw Data:', rawData); // Optional: Log raw data for debugging
    console.log('Hashed Data:', hashedData); // Log the SHA-512 hash

    return hashedData; // Return the hashed fingerprint
};

export default generateFingerprint;