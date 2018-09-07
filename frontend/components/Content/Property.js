import Link from 'next/link'
import Title from "../Content/Title"
import PropertyIcon from "../Content/PropertyIcon"
import React from 'react'

const Property = () => (
    <div id = "header_container" className = "row mb-5 mr-5 ml-3 property-container">
        <div className="col-sm-7 col-7 pl-0 propertyImg">
            <div className="pl-3 arrows">
                <img src = "../static/images/arrow_left.png" className="float-left"/>
                <img src = "../static/images/arrow_right.png" className="float-right"/>
            </div>
           
        </div>
        <div className="col-sm-5 col-5">
            <Title tstyle="des_title" title="St Kilda" />
            <Title tstyle="prop_address" title="23 Baker Street" />
            <div className="row px-2 d-flex justify-content-around">
                <PropertyIcon imgname="1-layers" value="4"/>
                <PropertyIcon imgname="2-layers" value="2"/>
                <PropertyIcon imgname="3-layers" value="1"/>
            </div>
            <Title tstyle="prop_value" title="$900,000" />
        </div>
    </div>

)
export default Property