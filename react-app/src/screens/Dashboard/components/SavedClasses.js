import React, { useEffect, useState } from "react";
import useApi from "src/hooks/useApi";
import useHashedId from "src/hooks/useHashedId";
import styled from "styled-components";
import TableHeader from "./TableHeader";
import TableRow from "./TableRow";

const TEST_DATA = [
  {
    id: "1",
    classTitle: "Information Chaos: Navigating Today's Information Landscape",
    courseCode: "ALS 1200",
    priorOfferings: "SP21 (A. Shea), SP20 (A. Shea), FA19 (A. Shea)",
    link: "https://classes.cornell.edu/browse/roster/SP22/class/ALS/1200",
    desc: "Information and communications technologies are fundamentally transforming public and nonprofit sectors. This course combines 1) managerial topics: technology acquisition, outsourcing, project management, risk governance, digital strategies; 2) emerging technologies: social media, artificial intelligence, cloud, analytics, big data; 3) real-life cases from global markets; 4) analytical and problem-solving frameworks. This course doesn't require technical background.",
  },
  {
    id: "2",
    classTitle: "Information Policy: Applied Research and Analysis",
    courseCode: "OMM 4201, INFO 4200, STS 4200",
    priorOfferings: "SP21 (A. Shea), SP20 (A. Shea), FA19 (A. Shea)",
    link: "https://classes.cornell.edu/browse/roster/SP22/class/ALS/1200",
    desc: "Information and communications technologies are fundamentally transforming public and nonprofit sectors. This course combines 1) managerial topics: technology acquisition, outsourcing, project management, risk governance, digital strategies; 2) emerging technologies: social media, artificial intelligence, cloud, analytics, big data; 3) real-life cases from global markets; 4) analytical and problem-solving frameworks. This course doesn't require technical background.",
  },
  {
    id: "3",
    classTitle: "Mathematical Foundations for the Information Age",
    courseCode: "CS 4850",
    priorOfferings: "SP20 (J. Hopcroft)",
    link: "https://classes.cornell.edu/browse/roster/SP22/class/ALS/1200",
    desc: "Information and communications technologies are fundamentally transforming public and nonprofit sectors. This course combines 1) managerial topics: technology acquisition, outsourcing, project management, risk governance, digital strategies; 2) emerging technologies: social media, artificial intelligence, cloud, analytics, big data; 3) real-life cases from global markets; 4) analytical and problem-solving frameworks. This course doesn't require technical background.",
  },
  {
    id: "4",
    classTitle: "Business Computing",
    courseCode: "HADM 1740",
    priorOfferings:
      "FA21 (A. Whitmore), SP21 (A. Whitmore), FA20 (A. Whitmore), SP20 (M. McCarthy)",
    link: "https://classes.cornell.edu/browse/roster/SP22/class/ALS/1200",
    desc: "Information and communications technologies are fundamentally transforming public and nonprofit sectors. This course combines 1) managerial topics: technology acquisition, outsourcing, project management, risk governance, digital strategies; 2) emerging technologies: social media, artificial intelligence, cloud, analytics, big data; 3) real-life cases from global markets; 4) analytical and problem-solving frameworks. This course doesn't require technical background.",
  },
];

const SavedClasses = () => {
  const HEADERS = [
    {
      label: "Class Title",
      isUnderlined: false,
      width: "40%",
    },
    {
      label: "Course Code",
      isUnderlined: false,
      width: "25%",
    },
    {
      label: "Prior Offerings",
      isUnderlined: false,
      width: "30%",
    },
  ];

  const api = useApi();
  const { hashedId } = useHashedId();
  const [data, setData] = useState([]);


  const fetchData = async () => {
    const { data } = await api.post("/load_courses", {
      hashed_id: hashedId,
    });

    if (data) {
      const savedCourses = data?.map((course) => ({
        ...course,
        offerings: course?.offerings?.join(', ')
      }))
      setData(savedCourses)
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRemove = async (data) => {
    await api.post("/unsave_course", {
      hashed_id: hashedId,
      course_name: data?.course_name,
      search_id: data?.search_id
    });
    fetchData()
  };

  return (
    <Container>
      <TableHeader headers={HEADERS} />
      <RowContainer>
        {data?.map((data) => (
          <TableRow
            key={data.course_name}
            widths={["40%", "25%", "30%"]}
            data={data}
            columns={[
              {
                key: "course_title",
                link: (data) => data?.roster_links?.length > 0 ? data?.roster_links[0] : null,
              },
              {
                key: "course_name",
                link: (data) => data?.roster_links?.length > 0 ? data?.roster_links[0] : null,
              },
              {
                key: "offerings",
              },
            ]}
            dropdownContent={data.course_desc}
            keyword="class"
            onRemove={handleRemove}
            isClass={true}
          />
        ))}
      </RowContainer>
    </Container>
  );
};

const Container = styled.div`
  width: 100%;
`;

const RowContainer = styled.div`
  max-height: 500px;
  overflow: auto;
`;

export default SavedClasses;
