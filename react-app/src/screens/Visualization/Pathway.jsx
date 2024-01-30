import React, { useEffect, useState } from "react";
import useHashedId from 'src/hooks/useHashedId';
import useApi from 'src/hooks/useApi';
import styled from "styled-components";
import PathwayYear from "./PathwayYear";
import useRouter from 'src/hooks/useRouter';

const Pathway = ({ searchId, pathway, colorCodes, vis_page, isSinglePathwayView,fullView=false }) => {
  const idxToYearLabel = [
    "1st Year",
    "2nd Year",
    "3rd Year",
    "4th Year",
    "5th Year",
  ];
  const coursesByYear = [];

  if (pathway?.courses) {
    Object.values(pathway?.courses)?.forEach((courseArray, idx) => {
      if (idx % 2 === 0) {
        coursesByYear.push([courseArray]);
      } else {
        coursesByYear[coursesByYear?.length - 1].push(courseArray);
      }
    });
  }


  const [savedCourses, setSavedCourses] = useState([]);
  const api = useApi();
  const { hashedId } = useHashedId();
  const router = useRouter()

  const fetchSavedpathways = async () => {
    const { data } = await api.post(`/load_courses`, {
      hashed_id: hashedId
    })

    if (data) {
      const courses = {}
      data?.map((course) => {
        courses[course?.course_name] = course
      })
      setSavedCourses(courses)
    }
  }

  useEffect(() => {
    fetchSavedpathways()
  }, [router?.query?.page])

  if (!pathway) return null;


  return (
    <Container>
      {coursesByYear?.map((courses, idx) => (
        <PathwayYear
          key={idxToYearLabel[idx]}
          yearLabel={idxToYearLabel[idx]}
          courses={courses}
          colorCodes={colorCodes}
          pathwayId={pathway?.pathway_id}
          searchId={searchId}
          vis_page={vis_page}
          savedCourses={savedCourses}
          isSinglePathwayView={isSinglePathwayView}
          fullView={fullView}
        />
      ))}
    </Container>
  );
};

const Container = styled.div`
  margin-left: 10%;
  margin-right: 10%;
  width: 80%;
`;

export default Pathway;
