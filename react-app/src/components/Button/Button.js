import React from "react";
import styled from "styled-components";

const Button = ({ children, variant, leftIcon, ...rest }) => {
  if (variant === 'subtle') {
    return (
      <SubtleButton {...rest}>{children}</SubtleButton>
    )
  }
  else if (variant === 'outlined') {
    return (
      <OutlinedButton {...rest}>{children}</OutlinedButton>
    )
  }

  if (leftIcon) {
    return (
      <StyledButton {...rest}>{leftIcon}{children}</StyledButton>
    )
  }

  return <StyledButton {...rest}>{children}</StyledButton>;
};

const StyledButton = styled.button`
  background: #4f42b5;
  border-radius: 5px;
  display: inline-block;
  cursor: pointer;
  font-weight: ${(props) => props.fontWeight || "bold"};
  line-height: 27px;
  color: #f3f8ff;
  border: 1px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;

  /* color */
  background: ${(props) => props.color && props.color};

  & svg {
    margin-right: 0.5rem;
  }

  /* size === 'sm' */
  padding: ${(props) => {
    if (props.size === "sm") return `.5rem .8rem`;
    if (props.padding) return props.padding;
    return "14px 30px";
  }};
  font-size: ${(props) => {
    if (props.size === "sm") return "1.1rem";
    return props.fontSize || "17px";
  }};

  &:hover {
    background: #1d4784;
  }
`;

const SubtleButton = styled(StyledButton)`
  font-size: 14px;
  padding: .2rem .8rem;
  background: #FFFFFF;
  color: #4f42b5;

  &:hover {
    background: #E2E0F3;
  }
`;

const OutlinedButton = styled(StyledButton)`
  background: #FFFFFF;
  color: #4f42b5;
  border: 1px solid #4f42b5;

  &:hover {
    background: #E2E0F3;
  }
`;

export default Button;
