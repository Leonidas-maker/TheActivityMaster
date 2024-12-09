import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';
import "../global.css"

export default function App() {
  return (
    <View className='flex-1 items-center justify-center'>
      <Text className='text-blue-700'>Open up App.tsx to start working on your app!</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});