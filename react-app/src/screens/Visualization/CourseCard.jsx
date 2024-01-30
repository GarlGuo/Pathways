import Text from "src/components/Text";
import useApi from "src/hooks/useApi";
import useHashedId from "src/hooks/useHashedId";
import styled from "styled-components";
import { ReactComponent as StarOutlined } from "src/assets/svgs/star-outlined.svg";
import { ReactComponent as StarFilled } from "src/assets/svgs/star-filled.svg";
import FlexContainer from 'src/components/containers/FlexContainer';
import { useEffect, useState } from 'react';

const CourseCard = ({
  searchId,
  course_name,
  course_title,
  colorCodes,
  roster_link,
  pathwayId,
  vis_page,
  isSaved,
  isSinglePathwayView
}) => {
  let borderColor = colorCodes.MISC;

  Object.keys(colorCodes)?.forEach((subject) => {
    const firstDigitIdx = course_name.search(/\d/);
    const courseSubject = course_name?.substring(0, firstDigitIdx);
    if (courseSubject === subject) {
      borderColor = colorCodes[subject];
    }
  });

  const api = useApi();
  const { hashedId } = useHashedId();

  const handleRecordInteraction = async () => {
    try {
      if (isSinglePathwayView) {
        await api.post("/log_dashboard_course_interaction_in_pathway", {
          hashed_id: hashedId,
          search_id: searchId,
          pathway_id: pathwayId,
          course_name,
        });
      } else {
        await api.post("/record_user_course_interaction", {
          search_id: searchId,
          hashed_id: hashedId,
          course_name,
          pathway_id: pathwayId,
          visualization_position_index: vis_page
        });
      }
    } catch (error) {
      console.log("error", error);
    }
  };

  const [isSavedLocal, setIsSavedLocal] = useState(isSaved);

  useEffect(() => {
    setIsSavedLocal(isSaved)
  }, [isSaved])

  const handleSave = async () => {
    setIsSavedLocal(true)
    await api.post('/save_course', {
      hashed_id: hashedId,
      course_name,
      search_id: searchId,
      pathway_id: pathwayId,
      visualization_position_index: vis_page
    })
  }

  const handleUnsave = async () => {
    setIsSavedLocal(false)
    await api.post('/unsave_course', {
      hashed_id: hashedId,
      course_name,
      search_id: searchId
    })
  }


  return (
    <Container
      borderColor={borderColor}
      isMuted={!(roster_link && roster_link?.length > 0)}
    >
      <FlexContainer justifySpaceBetween>
        {roster_link && roster_link?.length > 0 && course_title !== 'na' ? (
          <a
            href={roster_link}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleRecordInteraction}
          >
            <CourseName>{course_name}</CourseName>
          </a>
        ) : (
          <NotOfferedCourseName>{course_name}</NotOfferedCourseName>
        )}
        <div>
          {isSavedLocal ? <StyledStarFilled onClick={handleUnsave} /> : <StyledStarOutlined onClick={handleSave} />}
        </div>
      </FlexContainer>
      {roster_link && roster_link?.length > 0 && course_title !== 'na' ? (
        <a
          href={roster_link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={handleRecordInteraction}
        >
          <CourseTitle>{course_title}</CourseTitle>
        </a>
      ) : (
        <NotOfferedCourseTitle>Not Offered Anymore</NotOfferedCourseTitle>
      )}
    </Container>
  );
};

const Container = styled.div`
  height: 120px;
  width: 150px;
  border: 10px solid #c4c4c4;
  border-radius: 20px;
  padding: 8px;
  flex-shrink: 0;
  flex-grow: 0;

  /* borderColor */
  border-color: ${(props) => props.borderColor && props.borderColor};

  /* isMuted */
  & p {
    opacity: ${(props) => props.isMuted && `.6`};
  }

  & a {
    margin: 0;
    padding: 0;
    display: inline;
  }
`;

const CourseName = styled(Text)`
  font-weight: 700;
  font-size: 0.9rem;

  &:hover {
    text-decoration: underline;
  }
`;

const NotOfferedCourseName = styled(Text)`
  font-weight: 700;
  font-size: 0.9rem;
  color: #909090;
`;

const CourseTitle = styled(Text)`
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.2;
  font-weight: 500;

  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;

  &:hover {
    text-decoration: underline;
  }
`;

const NotOfferedCourseTitle = styled(Text)`
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.2;
  font-weight: 500;
  color: #909090;

  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
`;

const StyledStarOutlined = styled(StarOutlined)`
  cursor: pointer;
  height: 20px;
  width: 20px;
`;

const StyledStarFilled = styled(StarFilled)`
  cursor: pointer;
  fill: #4f42b5;
  height: 20px;
  width: 20px;
`;

export default CourseCard;
