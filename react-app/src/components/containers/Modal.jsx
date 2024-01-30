import React from "react";
import { makeStyles } from "@mui/styles";
import MaterialModal from "@mui/material/Modal";
import Backdrop from "@mui/material/Backdrop";
import Fade from "@mui/material/Fade";
import styled from "styled-components";
import { ReactComponent as CloseRaw } from "src/assets/svgs/remove.svg";
import Text from '../Text';

const useStyles = makeStyles(() => ({
  modal: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    outline: "none !important",
    zIndex: '99',
  },
}));

const Modal = ({ isOpen, handleClose, children, isRemovePadding, title = '', ...rest }) => {
  const classes = useStyles();
  const maxWidth=rest.maxWidth

  return (
    <MaterialModal
      open={isOpen}
      onClose={handleClose}
      className={classes.modal}
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
      }}
      {...rest}
    >
      <Fade in={isOpen}>
        <Container maxWidth={maxWidth}>
          <TopRow>
            <Text variant='h4'>{title}</Text>
            <CloseSVG onClick={handleClose} />
          </TopRow>
          <Content isRemovePadding={isRemovePadding}>{children}</Content>
        </Container>
      </Fade>
    </MaterialModal>
  );
};

const Container = styled.div`
  background: white;
  outline: none !important;

  padding: 1rem;
  min-width: 30vw;
  max-width: ${(props) => props.maxWidth? "100vm":"90vm"};
  min-height: 150px;
  max-height: 90vh;
  border-radius: 8px;
  overflow: auto;
  z-index: 99;

  @media (min-width: ${(props) => props.theme.md}px) {
    width: unset;
    max-width: 80vw;
  }
`;

const TopRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const CloseSVG = styled(CloseRaw)`
  height: 1rem;
  width: 1rem;
  opacity: 0.7;
  cursor: pointer;
`;

const Content = styled.div`
  padding: 1rem;

  & > button {
    margin-top: 1rem;
  }

  // isRemovePadding
  padding: ${(props) => props.isRemovePadding && "0"};
`;

export default Modal;
