import Link from 'next/link'
import Meta from "../global/Meta";


const QuickLink = props => (
    <div className="row px-3     py-3">
       <div className="col-md-5">
            <h5>Company</h5>
            <h5>Our Team</h5>
            <h5>Careers at C&G</h5>
            <h5>Property Management</h5>
            <h5>Blog</h5>
            <h5>Terms & Conditions</h5>
            <h5>Privacy Policy</h5>
       </div>
       <div className="col-md-5">
            <h5>Buying</h5>
            <h5>Selling</h5>
            <h5>Renting</h5>
            <h5>Sales Inspections</h5>
            <h5>Rental Inspections</h5>
            <h5>New Developments</h5>
       </div>
    </div>

)
export default QuickLink

//export default props => <h1>{props.title-name}</h1>