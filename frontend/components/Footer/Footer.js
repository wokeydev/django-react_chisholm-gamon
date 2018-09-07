import Link from 'next/link'
import Title from "../Content/Title"
import TextDetail from "../Content/TextDetail"
import QuickLink from "../Content/QuickLink"
import Button from "../Content/Button"
import Input from "../Content/Input"
const linkStyle = {
  marginRight: 15
}

const Footer = () => (
    <div className = "row py-5 mt-5 footer-style d-flex justify-content-around office-container">
        <div className="col-md-4">
            <Title tstyle="footer-title" title="Quick links"/>
            <QuickLink/>
        </div>
        <div className="col-md-3 office-item ">
            <Title tstyle="footer-title" title="Our locations"/>
            <div className="row px-4">
            <TextDetail title="Elwood" description="90 Ormond Road, Elwood"/>
            <TextDetail title="Port Melbourne" description="1/103D Bay Street, Port Melbourne"/>
            <TextDetail title="Black Rock" description="3 Bluff Road, Black Rock"/>
            <TextDetail title="Mount Martha" description="7A Bay Road, Mount Martha"/>
            </div>
        </div>
        <div className="col-md-4">
            <Title tstyle="footer-title" title="Feel like a local"/>
            <div className="row px-4">
                <h3>All the latest bayside property and real estate news direct from our team to your inbox...</h3>
                <div className="col-md-12 ml-1 mt-3 pb-5 pl-0">
                    <div className="row justify-content-around">
                        <div className="col-md-7 px-0"><Input placeholder="Your email"/></div>
                        <div className="col-md-4 px-0"><Button name="Sign me up"/></div>
                    </div>
                    <h4 class="pt-5 mt-5">Data supplied by AgentBox</h4>
                    <h4 class="">Designed and built by TechEquipt</h4>
                </div>  
            </div>
        </div>
    </div>

)
export default Footer