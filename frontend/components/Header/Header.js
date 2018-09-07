import Link from 'next/link'

const linkStyle = {
  marginRight: 15
}

const Header = () => (
    <div id = "header_container" className = "row py-3">
        <nav className="navbar navbar-expand-lg navbar-light w-100 mx-5">
            <a className="navbar-brand" href="#">
                <img src = "../static/images/logo.png"/>
            </a>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>

            <div className="collapse navbar-collapse" id="navbarSupportedContent">
                <ul className="navbar-nav ml-auto">
                    <li className="nav-item">
                        <a className="nav-link" href="#">Sell<span>.</span></a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="#">Buy me<span>.</span></a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="#">Lease<span>.</span></a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="#">Rent me<span>.</span></a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="#">More<span>...</span></a>
                    </li>
                </ul>
            </div>
        </nav>
    </div>

)
export default Header