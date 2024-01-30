import React from "react";
import styled from "styled-components";

const OutlinedButton = ({ children, ...rest }) => {
  return <StyledButton {...rest}>{children}</StyledButton>;
};

const StyledButton = styled.button`
  font-weight: 800;
  font-size: 20px;
  line-height: 27px;
  color: #4f42b5;
  text-decoration: none;
  padding: 14px 30px;
  background: inherit;
  border: 1px solid #c9d7ea;
  border-radius: 5px;
  display: inline-block;
  cursor: pointer;

  /* isPrimaryBorder */
  border-color: ${(props) => props.isPrimaryBorder && "#4F42B5"};

  &:hover {
    background: #c9d7ea;
    border-color: #c9d7ea;

    /* isPrimaryBorder */
    border-color: ${(props) => props.isPrimaryBorder && "#4F42B5"};
  }
`;

export default OutlinedButton;
