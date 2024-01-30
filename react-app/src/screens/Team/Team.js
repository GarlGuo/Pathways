import React from "react";
import LandingFooter from "../../components/LandingFooter/LandingFooter";
import LandingHeader from "../../components/LandingHeader";
import rene from "./images/rene.png";
import mina from "./images/mina.png";
import wentao from "./images/wentao.png";
import al from "./images/al.png";
import arnaav from "./images/arnaav.png";
import bob from "./images/bob.png";
import "./Team.css";

const Team = () => {
    return (
        <div>
            <LandingHeader></LandingHeader>
            <div className="team-heading">
                <h1>Project Members</h1>
            </div>
            <div className="row">
                <div className="person">
                    <img src={rene}></img>
                    <h2>Rene Kizilcec</h2>
                    <p>
                        Assistant Professor, Computing and Information Science<br />
                        Director, Future of Learning Lab<br />
                        Instructor of INFO 4100 Learning Analytics
                    </p>
                </div>
                <div className="person">
                    <img src={mina}></img>
                    <h2>Mina Chen</h2>
                    <p>
                        PhD Student, Information Science<br />
                        Pathways Project Lead
                    </p>
                </div>
                <div className="person">
                    <img src={wentao}></img>
                    <h2>Wentao Guo</h2>
                    <p>BS &#8216;22, Computer Science</p>
                </div>
            </div>
            <div className="row">
                <div className="person">
                    <img src={arnaav}></img>
                    <h2>Arnaav Sareen</h2>
                    <p>BA &#8216;25, Computer Science</p>
                </div>
                <div className="person">
                    <img src={al}></img>
                    <h2>Al Palanuwech</h2>
                    <p>MEng &#8216;23, Computer Science</p>
                </div>
                <div className="person">
                    <img src={bob}></img>
                    <h2>Bob Zhang</h2>
                    <p>MPS &#8216;23, Information Science</p>
                </div>
            </div>
            <div className="team-heading">
                <h1>Former Members</h1>
            </div>
            <div className="row">
                <div className="person">
                    <h2>Jaehyung (Jay) Joo</h2>
                    <p>BS &#8216;24, Computer Science</p>
                </div>
                <div className="person">
                    <h2>Sofia (Hee Won) Yoon</h2>
                    <p>MEng &#8216;22, Computer Science</p>
                </div>
                <div className="person">
                    <h2>Andrew Xu</h2>
                    <p>BS &#8216;24, Computer Science</p>
                </div>
            </div>
            <div className="row">
                <div className="person">
                    <h2>Fynn Datoo</h2>
                    <p>BS &#8216;22, Computer Science</p>
                </div>
                <div className="person">
                    <h2>Yuanhao Zhu</h2>
                    <p>MPS &#8216;22, Information Science</p>
                </div>
                <div className="person">
                    <h2>Martha Brandt</h2>
                    <p>MPS &#8216;21, Information Science</p>
                </div>
            </div>
            <div className="row">
                <div className="person">
                    <h2>Annie Fu</h2>
                    <p>BA &#8216;20, Information Science</p>
                </div>
                <div className="person">
                    <h2>Rebecca Fu</h2>
                    <p>BS &#8216;21, Applied Economics and <br /> Management &amp; Information Science</p>
                </div>
                <div className="person">
                    <h2>Jennifer Lee</h2>
                    <p>MPS &#8216;21, Information Science</p>
                </div>
            </div>
            <div className="row">
                <div className="person">
                    <h2>Ian Wilkie Tomasik</h2>
                    <p>BS &#8216;21, Information Science</p>
                </div>
                <div className="person">
                    <h2>Calix Huang</h2>
                    <p>High School Senior</p>
                </div>
            </div>


            <div className="row" style={{ flexDirection: "column", textAlign: "center", alignItems: "center" }}>
                <h3 style={{ fontSize: 25 }}>Want to Get Involved?</h3>
                <button className="button" onClick={() => window.location = 'mailto:yc2669@cornell.edu'}>Contact Us</button>
            </div>

            <LandingFooter></LandingFooter>
        </div>
    );
};

export default Team;
