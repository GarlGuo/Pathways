import styled from "styled-components";

const FlexContainer = styled.div`
  display: flex;

  // justifyStart
  justify-content: ${(props) => props.justifyStart && "flex-start"};

  // justifySpaceBetween
  justify-content: ${(props) => props.justifySpaceBetween && "space-between"};

  // justifySpaceAround
  justify-content: ${(props) => props.justifySpaceAround && "space-around"};

  // justifyCenter
  justify-content: ${(props) => props.justifyCenter && "center"};

  // justifyEnd
  justify-content: ${(props) => props.justifyEnd && "flex-end"};

  // alignStart
  align-items: ${(props) => props.alignStart && "flex-start"};

  // alignCenter
  align-items: ${(props) => props.alignCenter && "center"};

  // alignEnd
  align-items: ${(props) => props.alignEnd && "flex-end"};

  // directionColumn
  flex-direction: ${(props) => props.directionColumn && "column"};

  // wrap
  flex-wrap: ${(props) => props.wrap && "wrap"};

  // fullWidth
  width: ${(props) => props.fullWidth && "100%"};

  // fullHeight
  height: ${(props) => props.fullHeight && "100%"};
`;

export default FlexContainer;
