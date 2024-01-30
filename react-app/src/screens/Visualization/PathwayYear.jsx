import React from "react";
import FlexContainer from "src/components/containers/FlexContainer";
import Text from "src/components/Text";
import styled from "styled-components";
import CourseCard from "./CourseCard";
import ScrollContainer from "react-indiana-drag-scroll";
import useRouter from "src/hooks/useRouter";

const PathwayYear = ({ yearLabel, courses, colorCodes, pathwayId, searchId, vis_page, savedCourses, isSinglePathwayView,fullView=false }) => {
  // fullView: whether or not to disable horizontal scrolling

  const subjects = Object.keys(colorCodes);
  subjects.reverse();
  const router = useRouter();

  const compareCourses = (courseA, courseB) => {
    const subjectA = courseA?.course_name?.slice(
      0,
      courseA?.course_name.search(/\d/)
    );
    const subjectB = courseB?.course_name?.slice(
      0,
      courseB?.course_name.search(/\d/)
    );
    const orderValueA = subjects.indexOf(subjectA);
    const orderValueB = subjects.indexOf(subjectB);

    if (orderValueB > orderValueA) return 1;
    if (orderValueB < orderValueA) return -1;
    return 0;
  };

  if (courses && courses[0]) courses[0].sort(compareCourses);
  if (courses && courses[1]) courses[1].sort(compareCourses);

  return (
    <Container fullView={fullView}>
      <YearLabelContainer>
        <Text variant="h6" color="#FFFFFF" fontWeight={700}>
          {yearLabel}
        </Text>
      </YearLabelContainer>
      <FlexContainer>
        <SemesterLabelContainer>
          <SemesterLabel>FALL</SemesterLabel>
        </SemesterLabelContainer>
        <RelativeContainer>
          <SubjectsContainer hideScrollbars={false} fullView={fullView}>
            {courses[0]?.map((course, idx) => (
              <CourseCard
                searchId={searchId}
                key={`${pathwayId}${course?.course_name}${router?.query?.page}${idx}`}
                colorCodes={colorCodes}
                pathwayId={pathwayId}
                vis_page={vis_page}
                isSaved={course?.course_name in savedCourses}
                isSinglePathwayView={isSinglePathwayView}
                {...course}
              />
            ))}
            {courses[0]?.length > 6 && <RightPadding />}
          </SubjectsContainer>
          {courses[0]?.length > 6 && !fullView && <RightFade />}
        </RelativeContainer>
      </FlexContainer>
      <FlexContainer>
        <SemesterLabelContainer>
          <SemesterLabel>SPRING</SemesterLabel>
        </SemesterLabelContainer>
        <RelativeContainer>
          <SubjectsContainer hideScrollbars={false} fullView={fullView}>
            {courses[1]?.map((course, idx) => (
              <CourseCard
                searchId={searchId}
                key={`${pathwayId}${course?.course_name}${router?.query?.page}${idx}`}
                colorCodes={colorCodes}
                pathwayId={pathwayId}
                vis_page={vis_page}
                isSaved={course?.course_name in savedCourses}
                isSinglePathwayView={isSinglePathwayView}
                {...course}
              />
            ))}
            {courses[0]?.length > 6 && <RightPadding />}
          </SubjectsContainer>
          {courses[1]?.length > 6 &&  !fullView &&<RightFade />}
        </RelativeContainer>
      </FlexContainer>
    </Container>
  );
};

const Container = styled.div`
  margin-bottom: 2rem;

  & > div {
    margin-bottom: 0.5rem;
  }
`;

const YearLabelContainer = styled.div`
  width: 100%;
  height: 37px;
  background: #3457d3;
  border-radius: 14px;
  padding-left: 1rem;
  display: flex;
  align-items: center;
`;

const SemesterLabelContainer = styled.div`
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid #3457d3;
  height: 120px;
  width: 38px;
  flex-shrink: 0;
`;

const SemesterLabel = styled(Text)`
  font-size: 16px;
  font-weight: bold;
  writing-mode: vertical-rl;
  transform: scale(-1);
  color: #3457d3;
`;

const RelativeContainer = styled.div`
  position: relative;
`;

const SubjectsContainer = styled(ScrollContainer)`
  display: flex;
  width: ${props => props.fullView ? "100%" : "1040px"};
  padding-bottom: 0.5rem;

  & > div {
    margin-left: 0.5rem;
  }
`;

const RightPadding = styled.div`
  width: 16px;
  flex-shrink: 0;
  flex-grow: 0;
`;

const RightFade = styled.div`
  height: 100%;
  width: 4%;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;

  /* Permalink - use to edit and share this gradient: https://colorzilla.com/gradient-editor/#ffffff+0,ffffff+100&0+0,1+100 */
  background: -moz-linear-gradient(
    left,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 1) 100%
  ); /* FF3.6-15 */
  background: -webkit-linear-gradient(
    left,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 1) 100%
  ); /* Chrome10-25,Safari5.1-6 */
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 1) 100%
  ); /* W3C, IE10+, FF16+, Chrome26+, Opera12+, Safari7+ */
  filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#00ffffff', endColorstr='#ffffff',GradientType=1 ); /* IE6-9 */
`;

export default PathwayYear;
