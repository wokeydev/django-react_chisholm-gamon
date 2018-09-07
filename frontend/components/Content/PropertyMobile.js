import Link from 'next/link'
import Title from "../Content/Title"
import PropertyIcon from "../Content/PropertyIcon"
import React from 'react'

const PropertyMobile = () => (
    <div id = "header_container" className = "row mb-3">
        <div className="col-sm-7 col-7 pl-0 propertyImg">
            <div className="pl-3 arrows">
                <img src = "../static/images/arrow_left.png" className="float-left"/>
                <img src = "../static/images/arrow_right.png" className="float-right"/>
            </div>
           
        </div>
        <div className="col-sm-5 col-5">
            <Title tstyle='prop-title' title="St Kilda" />
            <Title tstyle='prop-address' title="23 Baker Street" />
            <div className="row px-0">
                <PropertyIcon imgname="1-layers" value="4"/>
                <PropertyIcon imgname="2-layers" value="2"/>
                <PropertyIcon imgname="3-layers" value="1"/>
            </div>
            <Title tstyle='prop-value' title="$900,000" />
        </div>
    </div>

)
export default PropertyMobile