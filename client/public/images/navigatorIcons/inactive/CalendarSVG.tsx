import * as React from "react"
import Svg, { Path } from "react-native-svg"

function CalendarSVG(props: any) {
  return (
    <Svg
      xmlns="http://www.w3.org/2000/svg"
      data-name="Layer 1"
      viewBox="0 0 24 24"
      width={512}
      height={512}
      {...props}
    >
      <Path d="M8 12H6c-1.103 0-2 .897-2 2v2c0 1.103.897 2 2 2h2c1.103 0 2-.897 2-2v-2c0-1.103-.897-2-2-2zm-2 4v-2h2v2H6zM19 2h-1V1a1 1 0 10-2 0v1H8V1a1 1 0 10-2 0v1H5C2.243 2 0 4.243 0 7v12c0 2.757 2.243 5 5 5h14c2.757 0 5-2.243 5-5V7c0-2.757-2.243-5-5-5zM5 4h14c1.654 0 3 1.346 3 3v1H2V7c0-1.654 1.346-3 3-3zm14 18H5c-1.654 0-3-1.346-3-3v-9h20v9c0 1.654-1.346 3-3 3z" />
    </Svg>
  )
}

export default CalendarSVG