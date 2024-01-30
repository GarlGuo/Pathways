
import React, { useState } from 'react'
import styled from 'styled-components'
import Button from './Button'
import Modal from './containers/Modal'
import { Space, Textarea } from '@mantine/core';
import FlexContainer from './containers/FlexContainer';
import useApi from 'src/hooks/useApi';
import useHashedId from 'src/hooks/useHashedId';
import RateReviewIcon from '@mui/icons-material/RateReview';

const FeedbackModalButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [value, setValue] = useState('');
  const api = useApi()
  const { hashedId } = useHashedId()

  const handleSubmit = async () => {
    api.post('/set_feedback', {
      hashed_id: hashedId,
      feedback: value
    })
    setValue('')
    setIsOpen(false)
  }

  return (
    <Container>
      <FeedbackButton size='sm' onClick={() => setIsOpen(true)} leftIcon={<StyledRateReviewIcon />} color='#EFC646'>Give feedback</FeedbackButton>
      <Modal
        isOpen={isOpen}
        handleClose={() => setIsOpen(false)}
        title="We'd love to hear your feedback!"
        isRemovePadding={true}
      >
        <Content>
          <Space mb='md' />
          <Textarea
            placeholder="What did you think about Pathways?"
            value={value}
            onChange={(event) => setValue(event?.target?.value)}
            minRows={5}
            autosize={true}
          />
          <Space mb='md' />
          <FlexContainer justifyEnd>
            <Button size='sm' onClick={handleSubmit}>Submit</Button>
          </FlexContainer>
        </Content>
      </Modal>
    </Container>
  )
}

const Container = styled.div`
  position: fixed;
  bottom: 1.5rem;
  left: 1.5rem;
  z-index: 98;
`

const Content = styled.div`
  width: 50vw;
  max-width: 500px;
`;

const StyledRateReviewIcon = styled(RateReviewIcon)`
  margin-top: 3px;
`;

const FeedbackButton = styled(Button)`
  font-size: .9rem;
`;

export default FeedbackModalButton
