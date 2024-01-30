import Button from "src/components/Button";
import OutlinedButton from "src/components/Button/OutlinedButton";
import FlexContainer from "src/components/containers/FlexContainer";
import Modal from "src/components/containers/Modal";
import Spacer from "src/components/Spacer";
import Text from "src/components/Text";
import useApi from 'src/hooks/useApi';
import useHashedId from 'src/hooks/useHashedId';
import styled from "styled-components";

const UnsaveModal = ({ handleClose, isOpen, pathwayId, pathwayName, searchId, ...rest }) => {
  const api = useApi();
  const { hashedId } = useHashedId()

  const handleUnsavePathway = async () => {
    await api.post("/unsave_pathway", {
      hashed_id: hashedId,
      pathway_id: pathwayId,
      search_id: searchId,
      name: pathwayName
    });
    handleClose()
  }

  return (
    <Modal handleClose={handleClose} isOpen={isOpen} {...rest}>
      <Text variant="h4" fontWeight="bold">
        Are you sure you would like to unsave this pathway?
      </Text>
      <Spacer y={0.5} />
      <Text variant="p">
        Once unsaved, this pathway will be removed from your Dashboard as body.
      </Text>
      <Spacer y={2} />
      <ButtonContainer>
        <Button onClick={handleUnsavePathway}>Unsave</Button>
        <Spacer x={1} />
        <OutlinedButton onClick={handleClose}>Cancel</OutlinedButton>
      </ButtonContainer>
    </Modal>
  );
};

const ButtonContainer = styled(FlexContainer)`
  & button {
    flex-grow: 2;
  }
`;

export default UnsaveModal;
