import Constants from 'expo-constants';


function getExpoDevServerIp(): string | null {
if (__DEV__) {
    const manifest = Constants.manifest || Constants.manifest2?.extra?.expoGo?.debuggerHost;
    if (manifest) {
    // Extrahiere die Host-IP-Adresse aus der Manifest-URL
    const debuggerHost = typeof manifest === 'string' ? manifest : (manifest as any).debuggerHost;
    const match = debuggerHost?.match(/^(.*):\d+$/);
    return match ? match[1] : null;
    }
}
return null; 
}
export default getExpoDevServerIp;


