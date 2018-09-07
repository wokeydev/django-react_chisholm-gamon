import Meta from "../global/Meta";
import Header from "../Header/Header"
import Title from "../Content/Title"
import Property from "../Content/Property"
import PropertyMobile from "../Content/PropertyMobile"
import TextDetail from "../Content/TextDetail"
import Button from "../Content/Button"
import Footer from "../Footer/Footer"
import FooterLink from "../Footer/FooterLink"

const MobileMain = () => (
    <div>
        <div className = "container-fluid px-0 mobile-container">
            <div className="row d-flex justify-content-around">
                <a className="py-3" href="#"><img src = "../static/images/logo-mobile.png"/></a>
            </div>
            <div className="row justify-content-around mx-0">
                <img className="" src = "../static/images/office-elwood-mobile.png"/>
            </div>
            <div className="row ml-0 px-2 description-wrapper description-wrapper-mobile">
                    <h1 className="w-100 text-center">PAGE TITLE</h1>
                    <h2 className="w-100 text-center">Page Subtitle</h2>
                    <p className="w-100 d-inline-block " style={{maxHeight:300}}>
                    Cras quis nulla commodo, aliquam lectus sed, blandit augue. Cras ullamcorper bibendum bibendum. Duis tincidunCras ullamcorper bibendum bibendum.Cras ullamcorper bibendum bibendum.Cras ullamcorper bibendum bibendum.Cras ullamcorper bibendum bibendum.
                    </p>
            </div>
            <div className="col-12 office-container">
                <div className="row">
                <Title tstyle="property-title" title="LATEST PROPERTIES"/>
                <div className="col-md-12 col-sm-12">
                    <PropertyMobile />
                    <PropertyMobile/>
                    <PropertyMobile/>
                    <Title tstyle="prop-title" title="View All"/>
                </div>
                </div>
            </div>
            <div className="col-12">
                <div className="row px-4">
                    <Title tstyle='mobile-title' mobile-title title="OUR OFFICES"/>
                    <Title tstyle='mobile-subtitle' title="Elwood"/>
                    <Title tstyle='mobile-subtitle' title="Port Melbourne"/>
                    <Title tstyle='mobile-subtitle' title="Black Rock"/>
                    <Title tstyle='mobile-subtitle' title="Mount Martha"/>
                </div>
            </div>
            <div className="col-12 mt-3">
                <div className="row px-4">
                    <Title tstyle='mobile-title' title="FIND IT FAST"/>
                    <Title tstyle='mobile-subtitle' title="What's my home worth?"/>
                    <Title tstyle='mobile-subtitle' title="Time for something new"/>
                    <Title tstyle='mobile-subtitle' title="I'm here for business"/>
                    <Title tstyle='mobile-subtitle' title="Bayside living"/>
                    <Title tstyle='mobile-subtitle' title="Work with us"/>
                </div>
            </div>
            <div className="col-12 mt-3 mb-4">
                <div className="row">
                    <Title className="w-100" tstyle="mobile-title" title="Move your property fast with a bayside professional property appraisal"/>
                    <div className="col-12">
                        <div className="row d-flex justify-content-around">
                            <div className="col-5"><Button name="Sell"/></div>
                            <div className="col--5"><Button name="Rental"/></div>
                        </div>
                    </div>
                </div>
            </div>
            <FooterLink />
            <div className="col-12 py-2 pl-5" style={{backgroundColor:'black'}}>
                <span style={{fontSize:14,color:'white'}}>Teams&Conditions | Privacy</span>
            </div>
        </div>
    </div>
)

export default MobileMain