import styled from 'styled-components';
import { Text } from 'src/components/Text';

const CareerOutcomeCard = ({ data }) => {
  return (
    <Container>
      <CareerOutcomeCardContainer>
        <PostGradHeader>
          Post Graduation
        </PostGradHeader>
        {/* if employment sector is non-empty: they went to industry */}
        {data['employment_sector'] !== '' && <PostGradBody>
          <b> Employment Sector: </b> {data['employment_sector']} <br />
          <b> Field of Occupation: </b> {data['employment_field']}
        </PostGradBody>}
        {/* if grad degree is non-empty: they went to grad school */}
        {data['grad_degree'] !== '' && <PostGradBody>
          <b> Graduate Degree: </b> {data['grad_degree']} <br />
          <b> Field of Study: </b> {data['grad_field']}
        </PostGradBody>}
        {/* when both are undefined, they didn't report such info */}
        {data['grad_degree'] === '' && data['employment_sector'] === '' && <PostGradBody empty={true} >
          Unreported
        </PostGradBody>}
      </CareerOutcomeCardContainer>
    </Container>
  )
}

const Container = styled.div`
  margin-left: 10%;
  margin-right: 10%;
  width: 80%;
`;

const CareerOutcomeCardContainer = styled.div`
`;

// font should be bold
const PostGradHeader = styled(Text)`
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 24px;
  color: #FFFFFF;
  background-color: #4E8BC6;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 14px;
`;

const PostGradBody = styled.div`
  border: 5px solid #B7B2E0;
  font-size: 20px;
  border-radius: 14px;
  padding: 10px 30px;

  ${props => props.empty && `
    line-height: 3.9rem;
  `}
`;

export default CareerOutcomeCard;