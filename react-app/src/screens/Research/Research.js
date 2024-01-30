import React from "react";
import LandingFooter from "../../components/LandingFooter/LandingFooter";
import LandingHeader from "../../components/LandingHeader";
import logo from "./images/logo.svg";
import research from "./images/research.svg";
import contributions from "./images/contributions.svg";
import bubble1 from "./images/bubble1.svg";
import bubble2 from "./images/bubble2.svg";
import "./Research.css";

const Research = () => {
    return (
        <div>
            <LandingHeader></LandingHeader>
            <div style={{ maxWidth: 1800, margin: '0 auto' }}>
                <div className="heading">
                    <div>
                        <img src={logo} className="logo"></img>
                        <h1>As a Research Project</h1>
                    </div>
                    <img src={research} className="bigImage"></img>
                </div>
                <div className="bubbles">
                    <div className="bubble" style={{ backgroundColor: "#F1F1F1" }}>
                        <p>Academic exploration systems open up new avenues to provide guidance for course and major choices with the hope to promote accessibility, scalability and equity. It also raises new questions about the role technology plays in academic information-seeking and decision-making. </p>
                    </div>
                    <div className="bubble" style={{ backgroundColor: "#EAEDFB", marginTop: 50, marginLeft: "auto" }}>
                        <p>As a research project, we use both qualitative and quantitative methods to understand how academic pathways are shaped by its surrounding information ecosystem. Specifically, we study trends and patterns in search and exploration behaviors with data gathered through Pathways. We also investigate ways to develop algorithmic recommendations and psychological interventions that can better facilitate interest exploration and purpose development through academic journeys.</p>
                    </div>
                </div>
                <div className="contributions" style={{ marginBottom: 50 }}>
                    <div className="heading">
                        <img src={contributions} className="bigImage"></img>
                        <div><h1><i>Publications</i></h1></div>
                    </div>
                    <p>Chen, Y., Fu, A., Lee, J., Wilkie Tomaski, I., & Kizilcec, R. F. (accepted). Pathways: Exploring Academic Interests with Historical Course Enrollment Records. In <i>Proceedings of the ACM Conference on Learning at Scale</i>.</p>
                    <p style={{ backgroundColor: "#EAEDFB" }}>
                        Students who use Pathways enable our research. The knowledge we gain through Pathways is available to inform students’ decisions, teaching, and administration at Cornell, and the accumulation of scientific knowledge about choice and decision generally.
                        <br/><br/>
                        We collect information regarding user interactions with Pathways and analyze data at the aggregate level only. In the interest of research, users may also be exposed to survey questions and variations in the presentation of information in Pathways. The data we gathered through Pathways is deidentified and studied by linking it with other information about Cornell students collected through the University systems.
                    </p>
                </div>
            </div>
            <LandingFooter></LandingFooter>
        </div>
    );
};

export default Research;
