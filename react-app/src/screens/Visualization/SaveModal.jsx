import React, { useEffect, useState } from "react";
import Button from "src/components/Button";
import OutlinedButton from "src/components/Button/OutlinedButton";
import FlexContainer from "src/components/containers/FlexContainer";
import Modal from "src/components/containers/Modal";
import Spacer from "src/components/Spacer";
import Text from "src/components/Text";
import useApi from 'src/hooks/useApi';
import useHashedId from 'src/hooks/useHashedId';
import styled from "styled-components";

const SaveModal = ({ handleClose, isOpen, pathwayId, searchId, visualizationPositionIndex, minors, majors, courses, colorCodes, ...rest }) => {
  const [name, setName] = useState();
  const api = useApi();
  const { hashedId } = useHashedId()
  const [isLengthError, setIsLengthError] = useState(false);


  useEffect(() => {
    if (isOpen) {
      const now = new Date();
      const month = ("0" + String(now.getMonth())).slice(-2);
      const date = ("0" + String(now.getDate())).slice(-2);
      const defaultName = `${month}-${date}-${now.getFullYear()} ${now.getHours()}:${now.getMinutes()}:${now.getSeconds()} Pathway`;
      setName(defaultName);
    }
  }, [isOpen]);

  const colorCodedCourses = {}

  Object.entries(courses)?.forEach(([key, semesterCourses]) => {
    colorCodedCourses[key] = semesterCourses?.map((course) => {
        const firstDigitIdx = course?.course_name.search(/\d/);
        const subject = course?.course_name?.substring(0, firstDigitIdx);
        let subjectForColor = 'MISC'
        if (subject in colorCodes) subjectForColor = subject
        return {
          ...course,
          color: colorCodes[subjectForColor]
        }
    })
  })

  const handleSave = async () => {
    if (!name) return;

    if (name?.length > 100) {
      setIsLengthError(true)
      return
    }

    await api.post('/save_pathway', {
      hashed_id: hashedId,
      pathway_id: pathwayId,
      name,
      search_id: searchId,
      'visualization_position_index': visualizationPositionIndex,
      order_and_color: {
        pathway_id: pathwayId,
        minors,
        majors,
        courses: colorCodedCourses
      }
    })

    setIsLengthError(false)
    handleClose()
  };

  return (
    <Modal handleClose={handleClose} isOpen={isOpen} {...rest}>
      <Text variant="h6" fontWeight="bold">
        Save This Pathway
      </Text>
      <NameInput
        value={name}
        onChange={(event) => setName(event.target.value)}
      />
      {isLengthError && <ErrorMessage>The pathway name should be shorter than 100 characters</ErrorMessage>}
      <ButtonContainer>
        <Button onClick={handleSave}>Save</Button>
        <Spacer x={1} />
        <OutlinedButton onClick={handleClose}>Cancel</OutlinedButton>
      </ButtonContainer>
    </Modal>
  );
};

const NameInput = styled.input`
  font-size: 1.25rem;
  border: 1px solid #c9d7ea;
  border-radius: 5px;
  width: 516px;
  padding: 0.75rem 1rem;
  margin: 1rem 0;
`;

const ButtonContainer = styled(FlexContainer)`
  & button {
    flex-grow: 2;
  }
`;

const ErrorMessage = styled(Text)`
  color: #F03E3E;
  margin-bottom: 1rem;
`;

export default SaveModal;
