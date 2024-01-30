import React, { useEffect, useState } from "react";
import useApi from "src/hooks/useApi";
import useHashedId from "src/hooks/useHashedId";
import styled from "styled-components";
import TableHeader from "../TableHeader";
import TableRow from "../TableRow";

const TEST_DATA = [
  {
    id: "1",
    interest: "pathway interest 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    searchTime: "2021/09/21 10:00PM",
  },
  {
    id: "2",
    interest: "pathway interest 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    searchTime: "2021/09/21 10:00PM",
  },
  {
    id: "3",
    interest: "pathway interest 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    searchTime: "2021/09/21 10:00PM",
  },
  {
    id: "4",
    interest: "pathway interest 1",
    major: "Cognitive Science, Computer Science, Molecular and Cell Biology",
    searchTime: "2021/09/21 10:00PM",
  },
];

const HEADERS = [
  {
    label: "Interest",
    isUnderlined: false,
    width: "40%",
  },
  {
    label: "Major",
    isUnderlined: false,
    width: "40%",
  },
  {
    label: "Search Time",
    isUnderlined: false,
    width: "20%",
  },
];

const SearchHistory = () => {
  const [data, setData] = useState();

  const api = useApi();
  const { hashedId } = useHashedId();

  const fetchData = async () => {
    const { data } = await api.post("/get_history", {
      hashed_id: hashedId,
    });
    setData(data?.map((searchHistory) => ({
      ...searchHistory,
      date: searchHistory?.date?.replace('GMT', 'ET')
    })));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRemove = async (data) => {
    await api.post("/unsave_history", {
      hashed_id: hashedId,
      _id: data?._id,
      search_id: data?.search_id
    });
    fetchData()
  };

  return (
    <Container>
      <TableHeader headers={HEADERS} />
      <RowContainer>
        {data &&
          data.map((history) => (
            <TableRow
              key={data.id}
              widths={["40%", "40%", "20%"]}
              data={history}
              columns={[
                {
                  key: "interest_keywords",
                  isArray: true,
                },
                {
                  key: "majors",
                  isArray: true,
                },
                {
                  key: "date",
                },
              ]}
              keyword="history"
              onRemove={handleRemove}
              isHistory={true}
            />
          ))}
      </RowContainer>
    </Container>
  );
};

const Container = styled.div``;

const RowContainer = styled.div`
  max-height: 500px;
  overflow: auto;
`;

export default SearchHistory;
