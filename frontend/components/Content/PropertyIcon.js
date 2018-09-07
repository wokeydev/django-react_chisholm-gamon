import Link from 'next/link'
import Title from "../Content/Title"


const PropertyIcon = props => (
    <div className="col-sm-4 col-4 rounded-circle border shadow pt-1 bg-white propertyIcon-container">
        <img className="mx-auto d-block " src = {`../static/images/${props.imgname}.png`}/>
        <h5 className="text-center" style={{fontSize:18}}>{props.value}</h5>
    </div>

)
export default PropertyIcon