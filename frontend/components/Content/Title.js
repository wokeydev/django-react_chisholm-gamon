import Link from 'next/link'
import Meta from "../global/Meta";
import React from 'react'

// const Title = props => (
//     <div className="w-100">
//        {/* <h1>{titleStyle}</h1> */}
//        <h1 className="text-center">{props.title}</h1>
//     </div>

// )
class Title extends React.Component {
  render() {
    return (
      <div className="w-100">
        <h1 className={this.props.tstyle}>{this.props.title}</h1>
     </div>
    )
  }
}
export default Title

//export default props => <h1>{props.title-name}</h1>