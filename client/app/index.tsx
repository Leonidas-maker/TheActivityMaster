import { registerRootComponent } from "expo";
import { StatusBar } from 'expo-status-bar';
import RootNavigator from '../src/routes/RootNavigator';
import "../global.css"
import { ThemeProvider } from '../src/provider/ThemeProvider';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import generateFingerprint from "../src/fingerprint/Fingerprint";
import { useEffect } from "react";
import "expo-dev-client";

export default function App() {
  useEffect(() => {
    generateFingerprint();
  }, []);

  return (
    <ThemeProvider>
      <GestureHandlerRootView>
        <SafeAreaProvider>
          <StatusBar style="auto" />
          <RootNavigator />
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ThemeProvider>
  );
}

registerRootComponent(App);