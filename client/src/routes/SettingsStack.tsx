import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import Settings from '../screens/settings/Settings';

const Stack = createStackNavigator();

const SettingsStack: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false
      }}>
      <Stack.Screen name="SettingsHome" component={Settings} />
    </Stack.Navigator>
  );
};

export default SettingsStack;