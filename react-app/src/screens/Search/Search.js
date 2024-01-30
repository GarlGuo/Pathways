import React, { useState, useEffect, useRef } from "react";
import ClipLoader from "react-spinners/ClipLoader";
import Nav from "../../components/Nav";
import "./Search.css";
import ConsentPopup from "./components/ConsentPopup/ConsentPopup";
import Header from "./components/Header";
import DeclaredMajor from "./components/DeclaredMajor";
import SelectMajor from "./components/SelectMajor";
import Interests from "./components/Interests";
import Courses from "./components/Courses";

import useLocalStorage from "src/hooks/useLocalStorage";
import useHashedId from "src/hooks/useHashedId";
import useApi from "src/hooks/useApi";

import sampleCourseBatch from "./data/sampleCourseBatch";
import Visualization from "../Visualization/Visualization";
import axios from "axios";
import useAuthRedirect from "src/hooks/useAuthRedirect";
import useRouter from "src/hooks/useRouter";
import { toPng } from "html-to-image";
import { useCallback } from "react";

import styled from "styled-components";
import { Text } from "src/components/Text";

const Search = () => {
  const [stepNumber, setStepNumber] = useState(0);
  const [searched, setSearched] = useState(false);
  const router = useRouter();

  // CONSENT POPUP
  const [consented, setConsented] = useLocalStorage("consented", false);

  // SCROLL TO VISUALIZATION
  const visualizationSectionRef = useRef(null);
  const scrollToRef = (ref) =>
    visualizationSectionRef.current.scrollIntoView({ behavior: "smooth" });

  const exportRef = useRef(null);

  const { hashedId } = useHashedId();
  const api = useApi();

  const [searchId, setSearchId] = useState(null);
  const [declaredMajor, setDeclaredMajor] = useState();
  const [majors, setMajors] = useState([]);
  const [otherMajor, setOtherMajor] = useState("");
  const [interests, setInterests] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [coursesDataLoaded, setCoursesDataLoaded] = useState(false);
  const [courseBatchesLoaded, setCourseBatchesLoaded] = useState(0);
  const [courses, setCourses] = useState([]);
  const [selectedCourses, setSelectedCourses] = useState([]);

  const [buttonDisabled, setButtonDisabled] = useState(false);
  const [exportData, setExportData] = useState({});

  const incrementStep = () => setStepNumber((stepNumber) => stepNumber + 1);
  const loadCourseBatch = async () => {
    setCoursesDataLoaded(false);
    setCoursesLoading(true);

    try {
      const { data } = await api.post("/get_suggested_courses", {
        search_id: searchId,
        hashed_id: hashedId,
        is_major_declared: declaredMajor,
        majors: majors.filter((m) => m !== "Other" && m !== "Undecided"),
        customized_majors: otherMajor,
        interest_keywords: interests,
        batch_number: courseBatchesLoaded,
      });

      setSelectedCourses([]);
      setCourses(data?.courses);
      setCourseBatchesLoaded((courseBatchesLoaded) => courseBatchesLoaded + 1);
      setCoursesDataLoaded(true);
      setCoursesLoading(false);
    } catch (error) {
      console.log("error", error);
    }
  };

  const nextStep = () => {
    switch (stepNumber) {
      case 1:
        if (declaredMajor !== undefined) {
          incrementStep();
        } else alert("Please specify if you've declared your major.");
        break;
      case 2:
        // REQUIRE MAJOR DATA IF NEEDED
        incrementStep();
        break;
      case 3:
        if (interests.length > 0) {
          incrementStep();
        } else alert("Please specify at least one interest.");
        break;
      default:
        // when 0
        incrementStep();
    }
  };

  const loadFirstPage = async () => {
    // on page load, generate the search ID
    const { data } = await api.post("/new_search_id", { hashed_id: hashedId });
    setSearchId(data["search_id"]);
    // reset page number on page reload
    router.updateQuery({ page: 1 });
  };

  const submitSearch = () => {
    setSearched(true);
    scrollToRef(visualizationSectionRef); // SCROLL TO VISUALIZATION
  };

  const reviseSearch = async () => {
    setSearchId(null);
    setSearched(false);
    setStepNumber(3);
    setCourses([]);
    setSelectedCourses([]);
    setCoursesDataLoaded(false);
    setCourseBatchesLoaded(0);
    setButtonDisabled(false);
    await loadFirstPage();
  };

  const startNewSearch = async () => {
    setSearchId(null);
    setSearched(false);
    setStepNumber(3);
    setInterests([]);
    setCoursesDataLoaded(false);
    setCourseBatchesLoaded(0);
    setCourses([]);
    setSelectedCourses([]);
    setButtonDisabled(false);
    await loadFirstPage();
  };

  const retrieveMajorHistory = async () => {
    //data is an array
    const { data } = await api.post("/get_history", { hashed_id: hashedId });
    if (!data?.length) return;
    // last updated entry
    const { is_major_declared, majors: retrievedMajors } = data[0];

    let majorSet = false;
    if (is_major_declared != null && declaredMajor === undefined) {
      setDeclaredMajor(is_major_declared);
      majorSet = true;
    }

    let retrievedMajorSet = false;
    if (retrievedMajors?.length && majors.length === 0) {
      setMajors(retrievedMajors);
      retrievedMajorSet = true;
    }

    if (majorSet && retrievedMajorSet) setStepNumber(3);
  };

  // attempts to fetch user's last major details
  useEffect(() => {
    if (declaredMajor === undefined || majors.length === 0)
      retrieveMajorHistory();

  }, []);
  useEffect(() => {
    if (stepNumber === 4) {
      loadCourseBatch();
      setCoursesDataLoaded(true);
    }
  }, [stepNumber]);

  useEffect(() => {
    if (stepNumber === 1 || stepNumber === 3) {
      setButtonDisabled(true);
    }

    if (stepNumber === 1) {
      setButtonDisabled(declaredMajor === undefined);
    }

    if (stepNumber === 3) {
      setButtonDisabled(interests.length === 0);
    }
  }, [stepNumber, declaredMajor, interests]);

  // AUTH REDIRECT
  const { setAuthRedirect } = useAuthRedirect();

  useEffect(() => {
    (async () => {
      if (!hashedId) {
        setAuthRedirect("/search");
        const endpoint =
          process.env.NODE_ENV === "production" ? "/api/auth/sso" : "/auth/sso";
        const { data } = await axios.post(endpoint);
        window.location.replace(data["url"]);
      } else {
        // on page load, generate the search ID
        const { data } = await api.post("/new_search_id", {
          hashed_id: hashedId,
        });
        setSearchId(data["search_id"]);
        // reset page number on page reload
        router.updateQuery({ page: 1 });
      }
    })();
  }, []);

  // POPULATE HISTORY DATA FROM DASHBOARD
  const [historyData, setHistoryData] = useLocalStorage("history-data", null);

  useEffect(() => {
    if (historyData) {
      switch (stepNumber) {
        case 0: {
          setDeclaredMajor(historyData?.is_major_declared);
          nextStep();
          break;
        }
        case 1: {
          setMajors(historyData?.majors);
          nextStep();
          break;
        }
        case 2: {
          setInterests(historyData?.interest_keywords);
          setHistoryData(null);
          nextStep();
          break;
        }
        default: {
          break;
        }
      }
    }
  }, [historyData, setHistoryData, stepNumber]);

  useEffect(() => {
    if (exportData) exportAsPng();
  }, [exportData]);

  const exportAsPng = useCallback(() => {
    let ref = exportRef;
    if (ref.current === null) {
      return;
    }
    // setTimeout to with 0 let DOM to load
    setTimeout(() => {
      toPng(ref.current, { backgroundColor: "white" })
        .then((dataUrl) => {
          const link = document.createElement("a");
          link.download = "my-schedule.png";
          link.href = dataUrl;
          link.click();
          setTimeout(() => {
            setExportData({});
          }, 0);
        })
        .catch((err) => {
          console.log(err);
        });
    }, 0);
  }, [exportRef]);

  return (
    <div>
      <ConsentPopup consented={consented} setConsented={setConsented} />

      <Nav></Nav>
      <div className="body-container">
        <Header />

        {/* STEP 1 - DECLARED MAJOR? */}
        {stepNumber >= 1 ? (
          <DeclaredMajor
            declaredMajor={declaredMajor}
            setDeclaredMajor={setDeclaredMajor}
            disabled={coursesDataLoaded || searched}
          />
        ) : (
          ""
        )}

        {/* STEP 2 - SELECT MAJOR(S) */}
        {stepNumber >= 2 ? (
          <SelectMajor
            declaredMajor={declaredMajor}
            majors={majors}
            setMajors={setMajors}
            otherMajor={otherMajor}
            setOtherMajor={setOtherMajor}
            disabled={coursesDataLoaded || searched}
          />
        ) : (
          ""
        )}

        {/* STEP 3 - DESCRIBE LEARNING INTERESTS, SELECT INTERESTSS */}
        {stepNumber >= 3 ? (
          <Interests
            interests={interests}
            setInterests={setInterests}
            disabled={coursesDataLoaded || searched}
          />
        ) : (
          ""
        )}

        {/* STEP 4 - VIEW AND SELECT COURSES */}
        {stepNumber == 4 ? (
          coursesLoading ? (
            <div style={{ textAlign: "center", padding: 30 }}>
              <ClipLoader color={"#4F42B5"} loading={true} size={40} />
            </div>
          ) : coursesDataLoaded ? (
            <Courses
              courses={courses}
              selectedCourses={selectedCourses}
              setSelectedCourses={setSelectedCourses}
              disabled={searched}
              loadCourseBatch={loadCourseBatch}
            />
          ) : (
            ""
          )
        ) : (
          ""
        )}

        {coursesDataLoaded ? (
          searched ? (
            <div
              style={{
                marginTop: 50,
                display: "flex",
                flexDirection: "row",
                justifyContent: "center",
              }}
            >
              <div style={{ textAlign: "center", marginRight: 15 }}>
                <button className="search-button" onClick={reviseSearch}>
                  Revise Search
                </button>
              </div>
              <div style={{ textAlign: "center" }}>
                <button className="search-button" onClick={startNewSearch}>
                  Start a New Search
                </button>
              </div>
            </div>
          ) : !coursesLoading && coursesDataLoaded ? (
            <div
              style={{
                marginTop: 50,
                display: "flex",
                flexDirection: "row",
                justifyContent: "center",
              }}
            >
              <div style={{ textAlign: "center", marginRight: 15 }}>
                <button
                  className="search-ghost-button"
                  onClick={() => {
                    setCourses([]);
                    setSelectedCourses([]);
                    setCoursesDataLoaded(false);
                    setStepNumber(3);
                    setCourseBatchesLoaded(0);
                  }}
                >
                  Back
                </button>
              </div>
              <div style={{ textAlign: "center" }}>
                <button className="search-button" onClick={submitSearch}>
                  Search
                </button>
              </div>
            </div>
          ) : (
            ""
          )
        ) : (
          <div style={{ textAlign: "right", marginTop: 50 }}>
            <button
              className="next-step-button"
              onClick={nextStep}
              disabled={buttonDisabled}
            >
              &rarr;
            </button>
          </div>
        )}
      </div>

      <div ref={visualizationSectionRef}>
        <Visualization
          searchId={searchId}
          searched={searched}
          is_major_declared={declaredMajor}
          majors={majors}
          interest_keywords={interests}
          suggested_courses={selectedCourses}
          otherMajor={otherMajor}
          setExportData={setExportData}
          exportData={exportData}
        />
      </div>

      {searched ? (
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "center",
            paddingBottom: "3rem",
          }}
        >
          <div style={{ textAlign: "center", marginRight: 15 }}>
            <button className="search-button" onClick={reviseSearch}>
              Revise Search
            </button>
          </div>
          <div style={{ textAlign: "center" }}>
            <button className="search-button" onClick={startNewSearch}>
              Start a New Search
            </button>
          </div>
        </div>
      ) : (
        ""
      )}

      {searched ? (
        <Resources>
          <ResourceHeader>Resources</ResourceHeader>
          <ResourceBody>
            <b> Looking for Career advice? </b>
            <ul>
              <li>
                {" "}
                Check out the{" "}
                <a
                  href="https://ccs.career.cornell.edu/dash/dashboard_activity"
                  target="_blank"
                >
                  {" "}
                  Career Dashboard
                </a>{" "}
                from Cornell’s Career Services Office.{" "}
              </li>
              <li>
                {" "}
                <a
                  href="https://scl.cornell.edu/get-involved/career-services/resources/about-us/cornell-career-network"
                  target="_blank"
                >
                  Schedule
                </a>{" "}
                an appointment with a career advisor.{" "}
              </li>
            </ul>
          </ResourceBody>
        </Resources>
      ) : (
        ""
      )}
      {Object.keys(exportData).length !== 0 ? (
        <div style={{ opacity: 0 }}>
          <div ref={exportRef}>
            <Visualization
              is_major_declared={true}
              majors={[]}
              searchId={exportData?.searchId}
              searched={true}
              interest_keywords={[""]}
              suggested_courses={[]}
              otherMajor={[]}
              isSinglePathwayView={true}
              pathwayId={exportData?.pathwayId}
              pathwayName={""}
              dataProvided={exportData}
              fullView={true}
            />
          </div>
        </div>
      ) : (
        ""
      )}
    </div>
  );
};

const Resources = styled.div`
  display: flex;
  flex-direction: column;
  margin-left: 10%;
  width: 80%;
`;

const ResourceHeader = styled(Text)`
  background-color: #d9d9d9;
  color: #5e5e5e;
  font-weight: bold;
  width: fit-content;
  padding: 0.5rem 1rem;
  margin-left: 1.5rem;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
`;

const ResourceBody = styled(Text)`
  border: 5px solid #4e8bc6;
  border-radius: 10px;
  padding-left: 1.25rem;
  padding-top: 1rem;
  margin-bottom: 3rem;
`;

export default Search;
