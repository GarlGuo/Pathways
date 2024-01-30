import axios from 'axios';
import { useEffect, useRef, useState } from "react";
import graduationImg from "src/assets/images/graduation.png";
import Button from 'src/components/Button';
import FlexContainer from "src/components/containers/FlexContainer";
import Text from "src/components/Text";
import useApi from "src/hooks/useApi";
import useDebouncedValue from 'src/hooks/useDebouncedValue';
import useHashedId from "src/hooks/useHashedId";
import useRouter from "src/hooks/useRouter";
import colorCodePathways from "src/util/colorCodePathways";
import styled from "styled-components";
import ColorLegend from "./ColorLegend";
import Pathway from "./Pathway";
import PathwayPagination from "./PathwayPagination";
import SaveModal from "./SaveModal";
import UnsaveModal from './UnsaveModal';
import ExportPathwayButton from './exportPathwayButton';
import CareerOutcomeCard from './CareerOutcomeCard';
import exportImg from "src/assets/images/save_24px.png";

const Visualization = ({
  searchId,
  searched,
  is_major_declared,
  majors,
  interest_keywords,
  suggested_courses,
  otherMajor,
  isSinglePathwayView,
  pathwayId,
  pathwayName,
  setExportData,
  dataProvided,
  fullView=false
}) => {
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [isUnsaveModalOpen, setIsUnsaveModalOpen] = useState(false);
  const [data, setData] = useState();
  const router = useRouter();
  const api = useApi();
  const { hashedId } = useHashedId();
  const [title, setTitle] = useState(pathwayName);
  const debouncedTitle = useDebouncedValue(title, 300)

  useEffect(() => {
    if (debouncedTitle) {
      api.post('/save_pathway', {
        hashed_id: hashedId,
        pathway_id: pathwayId,
        name: debouncedTitle,
        search_id: searchId,
        visualization_position_index: null,
        order_and_color: null
      })
    }
  }, [debouncedTitle])


  const fetchData = async () => {
    try {
      if (dataProvided!==undefined){
        setData({pathways:[dataProvided]})
        return
      }
      if (isSinglePathwayView) {
        const { data } = await api.post('/get_pathway', {
          hashed_id: hashedId,
          pathway_id: pathwayId,
          search_id: searchId,
        })
        setData({pathways: [data]})
      } else {
        const { data } = await api.post("/get_visualization", {
          search_id: searchId,
          hashed_id: hashedId,
          is_major_declared,
          majors,
          customized_majors: otherMajor,
          interest_keywords,
          suggested_courses,
        });
        setData(data);
      }
    } catch (error) {
      console.log("error", error);
    }
  };

  const colorCodesByPathway = colorCodePathways(data?.pathways);

  if (isSinglePathwayView && colorCodesByPathway && data?.pathways?.length === 1
     && colorCodesByPathway?.length === 1 && !dataProvided) {
    // overwrite colorCodes with those from backend
    Object.values(data?.pathways[0]?.courses)?.forEach((courseArr) => {
      courseArr?.forEach((course) => {
        const firstDigitIdx = course?.course_name.search(/\d/);
        const subject = course?.course_name?.substring(0, firstDigitIdx);
        if (subject in colorCodesByPathway[0]) {
          colorCodesByPathway[0][subject] = course?.color
        }
      })
    })
  }

  useEffect(() => {
    if (searched) {
      fetchData();
      // setData(samplePathways);
    }
  }, [searched]);

  // SCROLL TO VISUALIZATION
  const visualizationSectionRef = useRef(null);
  const scrollToRef = () =>{
    if (!dataProvided){
    visualizationSectionRef.current.scrollIntoView({ behavior: "smooth" })}};

  useEffect(() => {
    if (data) {
      scrollToRef();
      if (!isSinglePathwayView) {
        axios.post("/record_user_pathway_interaction", {
          "search_id": searchId,
          "hashed_id": hashedId,
          "pathway_id": data.pathways[0].pathway_id,
          "visualization_position_index": 1,
        })
      }
    }
  }, [data]);

  const pageIdx = isSinglePathwayView ? 1 : (router.query?.page || 1)

  // handle if pathway was already saved
  const [savedPathwayIds, setSavedPathwayIds] = useState([]);
  const isCurrentPathwaySaved = data?.pathways[pageIdx - 1]?.pathway_id in savedPathwayIds

  const fetchSavedPathways = async () => {
    const res = await api.post("/load_pathways", {
      hashed_id: hashedId,
    });
    const newSavedPathwayIds = {}
    res?.data?.forEach((pathway) => {
      newSavedPathwayIds[pathway?.pathway_id] = pathway
    })
    setSavedPathwayIds(newSavedPathwayIds)
  };

  useEffect(() => {
    fetchSavedPathways();
  }, []);

  




  const savePathwayButton = isCurrentPathwaySaved
    ? (
      <Button onClick={() => setIsUnsaveModalOpen(true)} {...exportButtonStyling}>
        <ExportImg src={exportImg} /> Unsave Course Schedule
      </Button>
    ) : (
      <Button variant='outlined' onClick={() => setIsSaveModalOpen(true)} {...exportButtonStyling}>
        <ExportImg src={exportImg} /> Save Course Schedule
      </Button>
    )
  
  if (!searched) return null;

  return (
    <div>
      {data && (
        <Container>
          <div ref={visualizationSectionRef} />
          {!isSinglePathwayView && (
            <Container>
              <Text variant="h2" style={{ textAlign: "center", margin: 0 }}>
                Explore Course Schedules from
              </Text>
              <Text variant="h2" style={{ textAlign: "center" }}>
                Previous Students at Cornell!
              </Text>
              <PathwayPagination
                searchId={searchId}
                all_pathway_data={data?.pathways}
                maxPages={data?.count}
              />
            </Container>
          )}
          <FlexContainer fullWidth>
            {isSinglePathwayView && (
              <PathwayTitleInput
                value={title}
                onChange={(event) => setTitle(event?.target?.value)}
              />
            )}
          </FlexContainer>
          {colorCodesByPathway && <ColorLegend
            colorCodes={colorCodesByPathway[pageIdx - 1]}
          />}
          <RowContainer>
            <FlexContainer alignCenter justifySpaceBetween fullWidth>
              <div>
                <Text>
                  Student Major:{" "}
                  {data?.pathways[pageIdx - 1]?.majors?.join(", ")}
                </Text>
                <Text>
                  {data?.pathways[pageIdx - 1]?.minors?.length > 0 &&
                    "Student Minor:"}{" "}
                  {data?.pathways[pageIdx - 1]?.minors?.join(", ")}
                </Text>
              </div>
              <FlexContainer>
              {!isSinglePathwayView && <ExportPathwayButton
              {...exportButtonStyling}
              data={data?.pathways[pageIdx - 1]}
              colorCodes={colorCodesByPathway && colorCodesByPathway[pageIdx - 1]}
              searchId={searchId}
              visualizationPositionIndex={0}
              setExportData={setExportData}
              />}
              {!isSinglePathwayView && savePathwayButton}
              </FlexContainer>
            </FlexContainer>
          </RowContainer>
          <Pathway
            pathway={data?.pathways[pageIdx - 1]}
            colorCodes={colorCodesByPathway[pageIdx - 1]}
            searchId={searchId}
            vis_page={pageIdx}
            isSinglePathwayView={isSinglePathwayView}
            fullView={fullView}
          />
          <GraduationImg src={graduationImg} />
          <CareerOutcomeCard data={data.pathways[pageIdx - 1]['career_outcome']} />
          {!isSinglePathwayView && <PathwayPagination
            searchId={searchId}
            all_pathway_data={data?.pathways}
            maxPages={data?.count}
          />}
        </Container>
      )}
      {data && colorCodesByPathway && <SaveModal
        isOpen={isSaveModalOpen}
        handleClose={() => {
          setIsSaveModalOpen(false)
          fetchSavedPathways()
        }}
        pathwayId={data?.pathways[pageIdx - 1]?.pathway_id}
        majors={data?.pathways[pageIdx - 1]?.majors}
        minors={data?.pathways[pageIdx - 1]?.minors}
        courses={data?.pathways[pageIdx - 1]?.courses}
        colorCodes={colorCodesByPathway && colorCodesByPathway[pageIdx - 1]}
        searchId={searchId}
        visualizationPositionIndex={null}
      />}
      {data && isUnsaveModalOpen && (
        <UnsaveModal
          isOpen={isUnsaveModalOpen}
          handleClose={() => {
            setIsUnsaveModalOpen(false)
            fetchSavedPathways()
          }}
          pathwayId={data?.pathways[pageIdx - 1]?.pathway_id}
          searchId={searchId}
          pathwayName={savedPathwayIds[data?.pathways[pageIdx - 1]?.pathway_id]?.name}
        />
      )}
    </div>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  & > * {
    margin-bottom: 3rem;
  }

  & a,
  a:hover,
  a:focus {
    text-decoration: none;
  }
`;

const DescText = styled(Text)`
  max-width: 1000px;
`;

const GraduationImg = styled.img`
  height: 130px;
  width: 210px;
`;


const RowContainer = styled.div`
  width: 100%;
  margin-bottom: 1.5rem;
  max-width: 1098px;
`;

const PathwayTitleInput = styled.input`
  margin-left: .2rem;
  border: none;
  font-size: 2rem;
  border-radius: 4px;
  padding: .2rem 1rem;
  width: 90%;
  cursor: pointer;

  &:hover {
    background: #F5F5F5;
  }
`;

const ExportImg = styled.img`
  height: 17px;
  width: 17px;
}
`;

const saveButtonStyling = {
  padding: '6px 20px',
  fontWeight: '500',
  fontSize: '17px'
}

const exportButtonStyling = {
  ...saveButtonStyling,
  style: { gap: 10, marginRight: 20 },
}
// .search-button {
//   color: white;
//   font-size: 17px;
//   font-weight: 500;
//   background-color: #4F42B5;
//   border: none;
//   border-radius: 5px;
//   padding: 10px 80px;
//   cursor: pointer;
// }

export default Visualization;
