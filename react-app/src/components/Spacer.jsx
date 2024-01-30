import styled from "styled-components";

export const Spacer = styled.div`
  flex-grow: 0;
  flex-shrink: 0;
  width: ${(props) =>
    props.x && (typeof props.x === "string" ? props.x : `${props.x}rem`)};
  height: ${(props) =>
    props.y && (typeof props.y === "string" ? props.y : `${props.y}rem`)};
`;

export default Spacer;
