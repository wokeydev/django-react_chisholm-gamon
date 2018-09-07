import Meta from "../components/global/Meta";
import Header from "../components/Header/Header"
import Title from "../components/Content/Title"
import Property from "../components/Content/Property"
import PropertyMobile from "../components/Content/PropertyMobile"
import TextDetail from "../components/Content/TextDetail"
import Button from "../components/Content/Button"
import Footer from "../components/Footer/Footer"
import FooterLink from "../components/Footer/FooterLink"
import MobileMain from "../components/Content/MobileMain"

import {
  BrowserView,
  MobileView,
  isBrowser,
  isMobile
} from "react-device-detect";


export default ({ children }) => (
  <div>
  <Meta />
  <BrowserView>
    <div className = "container-fluid browser-container">  
      <Header/>
      <div className="row">
        <div className="col-md-8 col-sm-12 pl-0">
          <div className="container-fluid pl-0">
            <div className="row ml-0">
              <img className="w-100 h-75" src = "../static/images/office-elwood.png"/>
            </div>
            <div className="row ml-0 description-wrapper">
              <h1 className="w-100 text-center">PAGE TITLE</h1>
              <h2 className="w-100 text-center">Page Subtitle</h2>
              <p className="m-5 w-100">
              Cras quis nulla commodo, aliquam lectus sed, blandit augue. Cras ullamcorper bibendum bibendum. Duis tincidunt urna non pretium porta. Nam condimentum vitae ligula vel ornare. Phasellus at semper turpis. Nunc eu tellus tortor. Etiam at condimentum nisl, vitae sagittis orci. Donec id dignissim nunc. Donec elit ante, eleifend a dolor et, venenatis facilisis dolor. In feugiat orci odio, sed lacinia sem elementum quis. Aliquam consectetur, eros et vulputate euismod, nunc leo tempor lacus, ac rhoncus neque eros nec lacus. Cras lobortis molestie faucibus. Cras quis nulla commodo, aliquam lectus sed, blandit augue. Cras ullamcorper bibendum bibendum. Duis tincidunt urna non pretium porta. Nam condimentum vitae ligula vel ornare. Phasellus at semper turpis. Nunc eu tellus tortor. Etiam at condimentum nisl, vitae sagittis orci. Donec id dignissim nunc. Donec elit ante, eleifend a dolor et, venenatis facilisis dolor. In feugiat orci odio, sed lacinia sem elementum quis. Aliquam consectetur, eros et vulputate euismod, nunc leo tempor lacus, ac rhoncus neque eros nec lacus. Cras lobortis molestie faucibus. 

              Cras quis nulla commodo, aliquam lectus sed, blandit augue. Cras ullamcorper bibendum bibendum. Duis tincidunt urna non pretium porta. Nam condimentum vitae ligula vel ornare. Phasellus at semper turpis. Nunc eu tellus tortor. Etiam at condimentum nisl, vitae sagittis orci. Donec id dignissim nunc. Donec elit ante, eleifend a dolor et, venenatis facilisis dolor. In feugiat orci odio, sed lacinia sem elementum quis. Aliquam consectetur, eros et vulputate euismod, nunc leo tempor lacus, ac rhoncus neque eros nec lacus. Cras lobortis molestie faucibus. Cras quis nulla commodo, aliquam lectus sed, blandit augue. Cras ullamcorper bibendum bibendum. Duis tincidunt urna non pretium porta. Nam condimentum vitae ligula vel ornare. Phasellus at semper turpis. Nunc eu tellus tortor. Etiam at condimentum nisl, vitae sagittis orci. Donec id dignissim nunc. Donec elit ante, eleifend a dolor et, venenatis facilisis dolor. In feugiat orci odio, sed lacinia sem elementum quis. Aliquam consectetur, eros et vulputate euismod, nunc leo tempor lacus, ac rhoncus neque eros nec lacus. Cras lobortis molestie faucibus.
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-4 col-sm-12 office-container">
          <div className="row">
            <Title tstyle="title" title="LATEST PROPERTIES"/>
            <div className="col-md-12 col-sm-12">
              <Property/>
              <Property/>
              <Property/>
              <Title tstyle="view_title" title="View All"/>
            </div>
          </div>
          <div className="row px-4">
            <Title tstyle="title" title="OUR OFFICES"/>
            <TextDetail tstyle="des_title" dstyle="des_txt" title="Elwood" description="90 Ormond Road, Elwood"/>
            <TextDetail tstyle="des_title" dstyle="des_txt" title="Port Melbourne" description="1/103D Bay Street, Port Melbourne"/>
            <TextDetail tstyle="des_title" dstyle="des_txt" title="Black Rock" description="3 Bluff Road, Black Rock"/>
            <TextDetail tstyle="des_title" dstyle="des_txt" title="Mount Martha" description="7A Bay Road, Mount Martha"/>
          </div>
          <div className="row px-4">
            <Title tstyle="title" title="FIND IT FAST"/>
            <TextDetail bstyle="des_border" tstyle="des_title" dstyle="des_txt"
                        title="What's my home worth?" description="Don't settle for less, get a free appraisal"/>
            <TextDetail bstyle="des_border" tstyle="des_title" dstyle="des_txt"
                        title="Time for something new" description="Buy a brand new property off the plan"/>
            <TextDetail bstyle="des_border" tstyle="des_title" dstyle="des_txt"
                        title="I'm here for business" description="Commercial properties and advice"/>
            <TextDetail bstyle="des_border" tstyle="des_title" dstyle="des_txt"
                        title="Bayside living" description="Learn local knowledge with our suburb profiles"/>
            <TextDetail bstyle="des_border" tstyle="des_title" dstyle="des_txt"
                        title="Work with us" description="We're always looking for amazing people"/>
          </div>
          <div className="row">
            <Title tstyle="title" title="Move your property fast with a bayside professional property appraisal"/>
            <div className="col-md-12 col-sm-12">
              <div className="row d-flex justify-content-around">
                <div className="col-md-5"><Button name="Sell"/></div>
                <div className="col-md-5"><Button name="Rental"/></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
      <FooterLink />
    </div>
  </BrowserView>
  <span></span>
  <MobileView>
    <MobileMain/>
  </MobileView>
  </div>
);