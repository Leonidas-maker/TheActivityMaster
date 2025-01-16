import * as React from "react"
import Svg, { Path } from "react-native-svg"

function ActiveCalendarSVG(props: any) {
  return (
    <Svg
      xmlns="http://www.w3.org/2000/svg"
      data-name="Layer 1"
      viewBox="0 0 24 24"
      width={512}
      height={512}
      {...props}
    >
      <Path d="M0 19c0 2.757 2.243 5 5 5h14c2.757 0 5-2.243 5-5v-9H0v9zm3-4c0-1.103.897-2 2-2h2c1.103 0 2 .897 2 2v2c0 1.103-.897 2-2 2H5c-1.103 0-2-.897-2-2v-2zm4.001 2H5v-2h2v2zM24 7v1H0V7c0-2.757 2.243-5 5-5h1V1a1 1 0 012 0v1h8V1a1 1 0 012 0v1h1c2.757 0 5 2.243 5 5z" />
    </Svg>
  )
}

export default ActiveCalendarSVG