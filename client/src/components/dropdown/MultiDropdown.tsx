// MultiDropdown.tsx
import React, { useState, useEffect } from "react";
import { View, useColorScheme, Text, ViewStyle, TextStyle } from "react-native";
import SectionedMultiSelect from "react-native-sectioned-multi-select";
import Icon from "react-native-vector-icons/MaterialIcons";

import { MultiDropdownProps } from "@/src/interfaces/componentInterfaces";

const MultiDropdown: React.FC<MultiDropdownProps> = ({
  setSelected,
  values,
  placeholder = "Select Permissions",
  notFound = "Please check your internet connection",
  useSections = true,
  searchPlaceholderText = "Search...",
  confirmButtonText = "Confirm",
}) => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const colorScheme = useColorScheme();
  const isLight = colorScheme === "light";

  const modalBgColor = isLight ? "#FFFFFF" : "#1C1C1E";
  const textColor = isLight ? "#000000" : "#FFFFFF";
  const boxBackground = isLight ? "#ACBED8" : "#56718A";
  const searchBarBg = isLight ? "#f0f0f0" : "#333333";
  const confirmButtonColor = "#3F51B5";

  const multiSelectColors = {
    primary: confirmButtonColor,
    text: textColor,
    subText: textColor,
    selectToggleTextColor: textColor,
    searchPlaceholderTextColor: isLight ? "#999" : "#ccc",
    searchSelectionColor: isLight ? "rgba(0,0,0,0.2)" : "rgba(255,255,255,0.2)",
    itemBackground: modalBgColor,
    subItemBackground: modalBgColor,
    chipColor: textColor,
  };

  const multiSelectStyles = {
    container: {
      backgroundColor: modalBgColor,
    } as ViewStyle,
    modalWrapper: {
      marginHorizontal: 20,
      marginVertical: 50,
      borderRadius: 10,
      overflow: "hidden",
      backgroundColor: modalBgColor,
    } as ViewStyle,
    listContainer: {
      backgroundColor: modalBgColor,
    } as ViewStyle,
    scrollView: {
      backgroundColor: modalBgColor,
    } as ViewStyle,
    item: {
      backgroundColor: modalBgColor,
    } as ViewStyle,
    subItem: {
      backgroundColor: modalBgColor,
    } as ViewStyle,
    itemText: {
      color: textColor,
      fontSize: 16,
    } as TextStyle,
    subItemText: {
      color: textColor,
      fontSize: 16,
    } as TextStyle,
    selectToggle: {
      backgroundColor: boxBackground,
      borderColor: boxBackground,
      borderWidth: 1,
      padding: 10,
      borderRadius: 10,
    } as ViewStyle,
    selectToggleText: {
      color: textColor,
      fontSize: 16,
    } as TextStyle,
    searchBar: {
      backgroundColor: searchBarBg,
      borderRadius: 4,
      margin: 10,
    } as ViewStyle,
    searchTextInput: {
      color: textColor,
    } as TextStyle,
    chipContainer: {
      backgroundColor: boxBackground,
      padding: 4,
      borderRadius: 8,
      margin: 2,
      borderWidth: 0,
    } as ViewStyle,
    chipText: {
      color: textColor,
      fontSize: 12,
    } as TextStyle,
    button: {
      backgroundColor: confirmButtonColor,
      margin: 10,
      borderRadius: 4,
    } as ViewStyle,
    confirmText: {
      color: "#FFFFFF",
      fontSize: 16,
      fontWeight: "600",
    } as TextStyle,
  };

  const items = useSections
    ? [
        {
          id: "0",
          name: "Options",
          children: values.map((item) => ({
            id: item.key,
            name: item.value,
          })),
        },
      ]
    : values.map((item) => ({
        id: item.key,
        name: item.value,
      }));

  const onSelectedItemsChange = (selected: any[]) => {
    setSelectedItems(selected);
    setSelected(selected);
  };

  return (
    <View className="w-3/4">
      <SectionedMultiSelect
        IconRenderer={Icon as any}
        items={items}
        uniqueKey="id"
        subKey={useSections ? "children" : undefined}
        selectText={placeholder}
        searchPlaceholderText={searchPlaceholderText}
        alwaysShowSelectText={true}
        renderSelectText={() => placeholder}
        selectedItems={selectedItems}
        onSelectedItemsChange={onSelectedItemsChange}
        colors={multiSelectColors}
        styles={multiSelectStyles}
        confirmText={confirmButtonText}
        noResultsComponent={
          <Text style={{ padding: 10, color: textColor }}>{notFound}</Text>
        }
      />
    </View>
  );
};

export default MultiDropdown;
