import { StatusBar } from 'expo-status-bar';
import "../../global.css"
import { ThemeProvider } from '../provider/ThemeProvider';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import generateFingerprint from "../fingerprint/Fingerprint";
import { useEffect } from "react";
import { Redirect } from "expo-router";

import "../custom_logger/custom_logger";

export default function Page() {
  useEffect(() => {
    generateFingerprint();
  }, []);

  return (
    <ThemeProvider>
      <GestureHandlerRootView>
        <SafeAreaProvider>
          <StatusBar style="auto" />
          <Redirect href="/(tabs)/DiscoverHome" />
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ThemeProvider>
  );
}