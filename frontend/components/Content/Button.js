import Link from 'next/link'


const PropertyIcon = props => (
    <div className="w-100">
        {/* <button type="button" className="btn btn-info center-block">Button</button> */}
        {/* <h1 className="text-center"><button type="button" className="btn btn-info btn-block mx-5">{props.name}</button></h1> */}
        <button type="button" className="btn btn-info btn-block yellowButton">{props.name}</button>
    </div>
)
export default PropertyIcon