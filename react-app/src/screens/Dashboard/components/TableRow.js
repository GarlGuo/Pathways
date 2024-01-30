import React, { useState } from "react";
import styled from "styled-components";
import removeSvg from "./../assets/remove.svg";
import dropdownSvg from "./../assets/dropdown.svg";
import ConfirmationModal from "src/components/containers/ConfirmationModal";
import Modal from 'src/components/containers/Modal';
import Visualization from 'src/screens/Visualization/Visualization';
import useApi from 'src/hooks/useApi';
import useHashedId from 'src/hooks/useHashedId';
import useLocalStorage from 'src/hooks/useLocalStorage';
import useRouter from 'src/hooks/useRouter';

const TableRow = ({
  columns,
  data,
  widths,
  dropdownContent,
  keyword,
  onRemove,
  isPathway,
  isHistory = false,
  isClass,
  isHoverStyles = true,
  onClosePathwayModal
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isPathwayModalOpen, setIsPathwayModalOpen] = useState(false);
  const api = useApi()
  const { hashedId } = useHashedId()
  const [historyData, setHistoryData] = useLocalStorage('history-data', null)
  const router = useRouter()

  const toggleExpanded = () => {
    if (!!dropdownContent) {
      setIsExpanded(!isExpanded);
    }
  };

  const handleClick = () => {
    if (isPathway) {
      setIsPathwayModalOpen(true)
    } else if (isHistory) {
      setHistoryData(data)
      router.push('/search')
    } else {
      toggleExpanded()
    }
  }

  const handleRemoveButtonClick = (event) => {
    event?.stopPropagation();
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
  };

  const handlePathwayModalClose = () => {
    setIsPathwayModalOpen(false)
    onClosePathwayModal()
  }

  const logInteraction = async () => {
    if (isClass) {
      await api.post("/log_dashboard_course_interaction", {
        hashed_id: hashedId,
        search_id: data?.search_id,
        course_name: data?.course_name,
      });
    }
  }

  return (
    <>
      <Container hasDropdown={!!dropdownContent} isExpanded={isExpanded} isHoverStyles={isHoverStyles}>
        <Row isExpanded={isExpanded} onClick={handleClick}>
          {!!dropdownContent ? (
            <DropdownButtonContainer>
              <DropdownButton src={dropdownSvg} isExpanded={isExpanded} />
            </DropdownButtonContainer>
          ) : (
            <Placeholder />
          )}
          <InnerRow>
            {columns.map((column, idx) => (
              <Column width={widths[idx]}>
                {column.link ? (
                  <StyledLink
                    target="_blank"
                    rel="noopener noreferrer"
                    href={column.link(data)}
                    onClick={logInteraction}
                  >
                    <ColumnText isUnderlined={Boolean(column.link(data))}>{column?.isArray ? data[column.key]?.join(', ') : data[column.key]}</ColumnText>
                  </StyledLink>
                ) : (
                  <ColumnText>{column?.isArray ? data[column.key]?.join(', ') : data[column.key]}</ColumnText>
                )}
              </Column>
            ))}
          </InnerRow>
          <RemoveButtonContainer onClick={handleRemoveButtonClick}>
            <RemoveButton src={removeSvg} />
          </RemoveButtonContainer>
        </Row>
        {isExpanded && dropdownContent && (
          <Dropdown>
            <DropdownText>{dropdownContent}</DropdownText>
          </Dropdown>
        )}
      </Container>
      <ConfirmationModal
        isOpen={isOpen}
        handleClose={closeModal}
        heading={`Are you sure you want to remove this ${keyword}?`}
        confirmText="Remove"
        cancelText={`Keep this ${keyword}`}
        onConfirm={() => {
          onRemove(data)
          closeModal()
        }}
      />
      <Modal
        isOpen={isPathwayModalOpen}
        handleClose={handlePathwayModalClose}
      >
        <VisualizationContainer>
          <Visualization
            is_major_declared={true}
            majors={[]}
            searchId={data?.search_id}
            searched={true}
            interest_keywords={[""]}
            suggested_courses={[]}
            otherMajor={[]}
            isSinglePathwayView={true}
            pathwayId={data?.pathway_id}
            pathwayName={data?.name}
          />
        </VisualizationContainer>
      </Modal>
    </>
  );
};

const RemoveButtonContainer = styled.div`
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.1s ease-in-out;
`;

const Container = styled.div`
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  transition: background-color 0.1s ease-in-out;
  border-radius: 8px;

  &:hover ${RemoveButtonContainer} {
    opacity: 1;
  }

  /* isHoverStyles */
  cursor: ${props => props?.isHoverStyles && 'pointer'};
  &:hover {
    background-color: ${props => props?.isHoverStyles && '#F5F5F5'};
  }
`;

const Row = styled.div`
  display: flex;
  align-items: flex-start;
  padding-bottom: ${(props) =>
    props.isExpanded && ".5rem"};
  border-bottom: ${(props) =>
    props.isExpanded && "1px solid rgba(0, 0, 0, .1)"};
`;

const InnerRow = styled.div`
  display: flex;
  flex-grow: 2;
`;

const Column = styled.div`
  width: ${(props) => props.width};
`;

const Dropdown = styled.div`
  transition: height 0.3s ease-in-out;
  padding-top: 0.5rem;
  padding-bottom: 1rem;
`;

const DropdownText = styled.p`
  font-size: 0.875rem;
  margin: 0;
`;

const ColumnText = styled.p`
  font-size: 0.875rem;
  text-decoration: ${(props) => props.isUnderlined && "underline"};
  margin: 0;
  display: inline-block;
`;

const Placeholder = styled.div`
  width: 2rem;
  flex-shrink: 0;
`;

const DropdownButtonContainer = styled.div`
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const DropdownButton = styled.img`
  margin-bottom: 0.2rem;
  transition: transform 0.3s;
  transform: ${(props) => props.isExpanded && "rotate(90deg)"};
`;

const RemoveButton = styled.img``;

const VisualizationContainer = styled.div`
  max-width: 90vw;
  overflow: auto;
`;

const StyledLink = styled.a`
  color: #4f42b5;
`;

export default TableRow;
