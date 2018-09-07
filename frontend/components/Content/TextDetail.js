import Link from 'next/link'
import Title from "../Content/Title"


const TextDetails = props => (
    <div class="row w-100 mb-3 office-item">
        <div className={"col-sm-8 " + props.bstyle}>
            <h2 className={props.tstyle}>{props.title}</h2>
            <h5 className={props.dstyle}>{props.description}</h5>
        </div>
        <div className="col-sm-4">
            <img className="arrow" src = "../static/images/arrow.png"/>
        </div>
    </div>
)
export default TextDetails