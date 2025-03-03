import * as React from "react"
import Svg, { Path } from "react-native-svg"

function ActiveClubSVG(props: any) {
  return (
    <Svg
      height={512}
      viewBox="0 0 24 24"
      width={512}
      xmlns="http://www.w3.org/2000/svg"
      data-name="Layer 1"
      {...props}
    >
      <Path d="M7.5 13A4.5 4.5 0 1112 8.5 4.505 4.505 0 017.5 13zM14 24H1a1 1 0 01-1-1v-.5a7.5 7.5 0 0115 0v.5a1 1 0 01-1 1zm3.5-15A4.5 4.5 0 1122 4.5 4.505 4.505 0 0117.5 9zm-1.421 2.021a6.825 6.825 0 00-4.67 2.831A9.537 9.537 0 0116.323 19H23a1 1 0 001-1v-.038a7.008 7.008 0 00-7.921-6.941z" />
    </Svg>
  )
}

export default ActiveClubSVG