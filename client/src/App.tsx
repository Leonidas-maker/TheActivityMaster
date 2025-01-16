import { registerRootComponent } from "expo";
import { StatusBar } from 'expo-status-bar';
import RootNavigator from './routes/RootNavigator';
import "../global.css"
import { ThemeProvider } from './provider/ThemeProvider';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function App() {
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