import "../../Search.css";
import "./ConsentPopup.css";

const ConsentPopup = ({ consented, setConsented }) => {
  return !consented ? (
    <div className="consent-background-container">
      <div className="consent-container">
        <h2 style={{ textAlign: "center" }}>Pathways is a Research Project</h2>
        <div className="consent-content">
          <p>We are building Pathways to learn about college pathways. The information we gather from your engagement with Pathways enables our research team to understand how students consider, choose, and sequence courses, and how these actions are related to other aspects of students' lives before, during, and after their time at Cornell. The knowledge we gain through Pathways is available to inform students' decisions, teaching and administration at Cornell, and the accumulation of scientific knowledge about choice and decision generally.</p>

          <p style={{ marginTop: 30 }}><strong>Your contributions:</strong> By using Pathways, you are volunteering for research. As you log in to Pathways, a hash identifier is assigned to track your usage. We track, collect and aggregate information regarding your interactions with Pathways including, among other things, the pages of the site you visit, the order and timing of your activities on Pathways, search terms, and the hyperlinks you "click". We also may ask you to answer some simple survey questions. In the interest of research, you may be exposed to some variation in the presentation of information available to you on the Pathways portal. You may stop participating in this research at any time by no longer using Pathways. Neither your academic progress nor program eligibility is contingent on your participation or non-participation in Pathways.</p>

          <p style={{ marginTop: 30 }}>We study the data we gather through Pathways by linking it with other information about Cornell students collected through other University systems. The data will be coded so that your name will be removed and replaced with a unique identifying code. We will neither identify you by name in any discussions or publications, nor describe data in such a way that you can be identified. </p>

          <p style={{ marginTop: 30 }}>While we cannot guarantee that you will receive any benefits from using Pathways, the potential benefits include giving you more information about course sequences and college pathways. There is minimal risk associated with participating in this research.</p>

          <p style={{ marginTop: 30 }}><strong>Our commitments:</strong> We use our research findings to continually improve Pathways and contribute to public discussion of educational improvement at Cornell and worldwide. In doing our work we consider and analyze data and report research findings at the aggregate level only. </p>

          <p style={{ marginTop: 30 }}>You can read this message again any time from a link at the bottom of the landing page. If you have questions about this research please contact Professor Rene Kizilcec at kizilcec@cornell.edu. If you have concerns about this research and would like to speak with someone independent of the research team, you may contact the Cornell IRB at irbhp@cornell.edu</p>
        </div>

        <div style={{ textAlign: "center", marginTop: 50 }}>
          <button
            className="search-button"
            onClick={() => setConsented(true)}
          >
            I agree
          </button>

          <span style={{ display: "block", color: "#555", marginTop: 30 }}>If you do not agree you may close this tab</span>
        </div>
      </div>
    </div>
  ) : ""
}

export default ConsentPopup;