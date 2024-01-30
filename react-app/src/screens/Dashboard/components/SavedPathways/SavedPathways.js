import React, { useEffect, useState } from "react";
import useApi from "src/hooks/useApi";
import useHashedId from "src/hooks/useHashedId";
import styled from "styled-components";
import TableHeader from "../TableHeader";
import TableRow from "../TableRow";

const TEST_DATA = [
  {
    id: "1",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "2",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "3",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "4",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "1",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "2",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "3",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "4",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "1",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "2",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "3",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "4",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "1",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "2",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "3",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "4",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "1",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "2",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "3",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
  {
    id: "4",
    name: "pathway name 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    minor: "Art, History, Data Science, Molecular and Cell Biology",
  },
];

const HEADERS = [
  {
    label: "Pathway Name",
    isUnderlined: false,
    width: "35%",
  },
  {
    label: "Major",
    isUnderlined: false,
    width: "30%",
  },
  {
    label: "Minor",
    isUnderlined: false,
    width: "35%",
  },
];

const SavedPathways = () => {
  const api = useApi();
  const { hashedId } = useHashedId();
  const [data, setData] = useState([]);

  const fetchData = async () => {
    const res = await api.post("/load_pathways", {
      hashed_id: hashedId,
    });
    setData(res?.data)
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRemove = async (data) => {
    await api.post("/unsave_pathway", {
      hashed_id: hashedId,
      pathway_id: data?.pathway_id,
      search_id: data?.search_id,
      name: data?.name
    });
    fetchData()
  };

  return (
    <Container>
      <TableHeader headers={HEADERS} />
      <RowContainer>
        {data?.map((data) => (
          <TableRow
            key={data.id}
            widths={["35%", "30%", "35%"]}
            data={data}
            columns={[
              {
                key: "name",
              },
              {
                key: "majors",
                isArray: true,
              },
              {
                key: "minors",
                isArray: true,
              },
            ]}
            keyword="pathway"
            onRemove={handleRemove}
            isPathway={true}
            onClosePathwayModal={fetchData}
          />
        ))}
      </RowContainer>
    </Container>
  );
};

const Container = styled.div`
`;

const RowContainer = styled.div`
  max-height: 500px;
  overflow: auto;
`;

export default SavedPathways;
