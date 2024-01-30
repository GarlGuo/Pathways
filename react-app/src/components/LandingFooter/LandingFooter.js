import React from "react";
import labLogo from "./images/lab-logo.svg";
import "./LandingFooter.css";

const LandingFooter = () => {
    return (
        <div className="footer">
            <h4>Built by the Future of Learning Lab</h4>
            <a href="https://learning.cis.cornell.edu"><img src={labLogo}></img></a>
        </div>
    );
};

export default LandingFooter;