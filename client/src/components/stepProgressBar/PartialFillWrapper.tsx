import React, { useState } from "react";
import { View } from "react-native";
import PartialFill from "./PartialFill";

interface PartialFillWrapperProps {
  fieldProgress: number;
}

const PartialFillWrapper: React.FC<PartialFillWrapperProps> = ({ fieldProgress }) => {
  const [containerWidth, setContainerWidth] = useState(0);

  return (
    <View
      className="h-full rounded-full overflow-hidden"
      onLayout={(event) => {
        setContainerWidth(event.nativeEvent.layout.width);
      }}
    >
      {containerWidth > 0 && (
        <PartialFill fieldProgress={fieldProgress} containerWidth={containerWidth} />
      )}
    </View>
  );
};

export default PartialFillWrapper;
