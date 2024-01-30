import React from "react";
import styled from "styled-components";

const TableHeader = ({ headers }) => {
  return (
    <Container>
      <Placeholder />
      <InnerRow>
        {headers.map((header) => (
          <Column
            key={header.label}
            width={header.width}
            isUnderlined={header.isUnderlined}
          >
            {header.label}
          </Column>
        ))}
      </InnerRow>
      <Placeholder />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  padding: 1rem;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
`;

const InnerRow = styled.div`
  display: flex;
  flex-grow: 2;
`;

const Column = styled.div`
  font-weight: bold;
  width: ${(props) => props.width};
  text-decoration: ${(props) => props.isUnderlined && "underline"};
`;

const Placeholder = styled.div`
  /* placeholder for buttons on the sides */
  width: 2rem;
  flex-shrink: 0;
`;

export default TableHeader;
