import { useEffect } from "react";
import useAuthExpire from 'src/hooks/useAuthExpire';
import useAuthRedirect from "src/hooks/useAuthRedirect";
import useHashedId from "src/hooks/useHashedId";
import useRouter from "src/hooks/useRouter";
import styled from "styled-components";
import Button from "../../components/Button";
import LandingFooter from "../../components/LandingFooter/LandingFooter";
import LandingHeader from "../../components/LandingHeader";
import explore from "./images/explore.svg";
import get from "./images/get.svg";
import laptop from "./images/laptop.png";
import learn from "./images/learn.svg";
import number1 from "./images/number1.svg";
import number2 from "./images/number2.svg";
import number3 from "./images/number3.svg";
import step1 from "./images/step1.svg";
import step2 from "./images/step2.svg";
import step3 from "./images/step3.svg";
import "./Landing.css";
import Personas from "./Personas";

const Item = ({ image, text }) => {
  return (
    <div className="item">
      <img src={image} />
      <p>{text}</p>
    </div>
  );
};

const Landing = () => {
  const router = useRouter();
  const { hashedId, setHashedId } = useHashedId();
  const { authRedirect, setAuthRedirect } = useAuthRedirect();
  const { setAuthExpire } = useAuthExpire();

  useEffect(() => {
    if (router?.query?.hashed_id) {
      setHashedId(router?.query?.hashed_id);
      const threeMonthsLater = new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 30 * 3)?.toString()
      setAuthExpire(threeMonthsLater)
      router?.updateQuery({}, true);

      if (authRedirect) {
        setAuthRedirect(null);
        router.push(authRedirect);
      }
    }
  }, [router, setHashedId, hashedId]);

  const handleGetStarted = async () => {
    router.push("/search");
  };

  return (
    <div>
      <LandingHeader></LandingHeader>
      <div className="row grey-background">
        <div className="left">
          <h2 className="sectionHeader">
            Explore your interest.
            <br />
            Find your Pathway.
          </h2>
          <p>Unlock all kinds of possibilities on your Cornell journey.</p>
          <GetStartedButton onClick={handleGetStarted}>
            Get started!
          </GetStartedButton>
        </div>
        <div className="right">
          <img src={laptop} alt="laptop" />
        </div>
      </div>
      <div style={{ width: "85%", margin: "auto" }}>
        <p className="pretitle centered"> What we offer </p>
        <h2 className="approach">
          A data driven approach to{" "}
          <span class="primaryColor">exploration</span>.
        </h2>
        <p className="centered textbody">
          It can be daunting to tackle your college career in the midst of
          information. <b>Pathways</b> uses past student decision records to
          help make that process smoother.
        </p>
        <div className="offerings">
          <Item
            image={explore}
            text="Explore your interests and goals by discovering new classes."
          />
          <Item
            image={learn}
            text="Learn about class and major decisions from other students like you."
          />
          <Item
            image={get}
            text="Connect ideas and get inspired for your career aspirations."
          />
        </div>
      </div>
      <div className="grey-background">
        <p className="pretitle2 centered"> Who we serve </p>
        <h2 className="personas" style={{ marginBottom: 32 }}>
          Built for students just like you.
        </h2>
        <Personas />
      </div>
      <div>
        <p className="pretitle centered"> Step-by-Step </p>
        <h2 className="approach">
          How we turn interests into <span class="primaryColor">Pathways</span>.
        </h2>

        <div className="step">
          <img src={step1} className="image"></img>
          <div className="textArea">
            <img src={number1} className="number"></img>
            <div className="text" style={{ bottom: -36 }}>
              <h3>Input Interests</h3>
              <p>
                Reflect on and write down a few sentences explaining your
                interests.
              </p>
            </div>
          </div>
        </div>

        <div className="step">
          <div className="textArea" style={{ marginRight: 84 }}>
            <div
              className="text"
              style={{ left: "unset", right: -100, bottom: -26 }}
            >
              <h3>Explore Classes</h3>
              <p>
                Explore and filter suggested courses based on your indicated
                interest.
              </p>
            </div>
            <img src={number2} className="number"></img>
          </div>
          <img src={step2} className="image"></img>
        </div>

        <div className="step">
          <img
            src={step3}
            className="image"
            style={{ width: "443px", height: "414px" }}
          ></img>
          <div className="textArea">
            <img src={number3} className="number"></img>
            <div className="text" style={{ bottom: -8 }}>
              <h3>View Pathways</h3>
              <p>
                View a diverse set of real student pathways that helps you
                explore your interest.
              </p>
            </div>
          </div>
        </div>
      </div>
      <LandingFooter></LandingFooter>
    </div>
  );
};

const GetStartedButton = styled(Button)`
  padding-left: 78.5px;
  padding-right: 78.5px;
  margin-top: 2rem;
`;

export default Landing;
