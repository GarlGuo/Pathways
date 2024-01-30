import React from "react";
import styled from "styled-components";
import Button from "../Button";
import OutlinedButton from "../Button/OutlinedButton";
import FlexContainer from "./FlexContainer";
import Modal from "./Modal";

const ConfirmationModal = ({
  isOpen,
  handleClose,
  isRemovePadding,
  heading,
  confirmText = "Confirm",
  cancelText = "Cancel",
  onConfirm,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      handleClose={handleClose}
      isRemovePadding={isRemovePadding}
    >
      <Container>
        <FlexContainer directionColumn alignCenter>
          <Heading>{heading}</Heading>
          <ButtonsContainer>
            <Button onClick={onConfirm}>{confirmText}</Button>
            <OutlinedButton onClick={handleClose}>{cancelText}</OutlinedButton>
          </ButtonsContainer>
        </FlexContainer>
      </Container>
    </Modal>
  );
};

const Container = styled.div`
  padding: 0 2rem;
`;

const Heading = styled.h2`
  font-size: 1.5rem;
  font-weight: 900;
  margin-bottom: 2rem;
`;

const ButtonsContainer = styled(FlexContainer)`
  & > *:first-of-type {
    margin-right: 0.5rem;
  }
`;

export default ConfirmationModal;
