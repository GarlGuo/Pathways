import React, { useEffect } from "react";
import styled from "styled-components";
import Pagination from "@mui/material/Pagination";
import useRouter from "src/hooks/useRouter";
import useHashedId from "src/hooks/useHashedId";
import useApi from "src/hooks/useApi";


const PathwayPagination = ({ searchId, all_pathway_data, maxPages }) => {
  const router = useRouter();
  const { hashedId } = useHashedId();
  const api = useApi();

  useEffect(() => {
    if (!router.query?.page) {
      router.updateQuery({ page: 1 });
    }
  }, []);

  const handleChange = (event, old_page, new_page) => {
    if (old_page !== new_page) {
      api.post("/record_user_pathway_interaction", {
        "search_id": searchId,
        "hashed_id": hashedId,
        "pathway_id": all_pathway_data[new_page - 1].pathway_id,
        visualization_position_index: new_page,
      })
      router.updateQuery({ page: new_page });
    }
  };

  return (
    <Container>
      <AnnotationText> Previous Student </AnnotationText>
      <Pagination
        variant="outlined"
        size="large"
        count={Number(maxPages)}
        page={Number(router.query?.page) || 1}
        onChange={(event, new_page) => handleChange(event, Number(router.query?.page), new_page)}
      />
      <AnnotationText> Next Student </AnnotationText>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: row;
`;

const AnnotationText = styled.p`
  font-size: 20px;
  margin-top: 0.3rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
`

export default PathwayPagination;
