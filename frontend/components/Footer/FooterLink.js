import Link from 'next/link'
import Title from "../Content/Title"
import TextDetail from "../Content/TextDetail"

const FooterLink = () => (
    <div className = "row px-0 py-5 footerlink-style">
        <div className="col-md-6 d-flex justify-content-around">
            <a href="#" className="footerLogo">
                <img src = "../static/images/footer_logo.png"/>
            </a>
        </div>
        <div className="col-md-6 col-12 justify-content-around px-0 mx-0">
            <a href="#" className="float-right ml-1">
                <img src = "../static/images/footer_5.png"/>
            </a>
            <a href="#" className="float-right ml-1">
                <img src = "../static/images/footer_4.png"/>
            </a>
            <a href="#" className="float-right ml-1">
                <img src = "../static/images/footer_3.png"/>
            </a>
            <a href="#" className="float-right ml-1">
                <img src = "../static/images/footer_2.png"/>
            </a> 
            <a href="#" className="float-right ml-1">
                <img src = "../static/images/footer_1.png"/>
            </a>
        </div>
    </div>

)
export default FooterLink