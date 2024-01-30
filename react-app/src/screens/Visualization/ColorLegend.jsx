import React from "react";
import FlexContainer from "src/components/containers/FlexContainer";
import Spacer from "src/components/Spacer";
import Text from "src/components/Text";
import styled from "styled-components";

const ColorLegend = ({ colorCodes }) => {
  if (!colorCodes) return null;

  const subjects = Object.keys(colorCodes);

  return (
    <Container>
      <FlexContainer alignCenter>
        <LegendItemContainer alignCenter>
          <ColoredCircle background={colorCodes[subjects[0]]} />
          <Text variant="h6" fontWeight="bold">
            {subjects[0]}
          </Text>
        </LegendItemContainer>
        <LegendItemContainer alignCenter>
          <ColoredCircle background={colorCodes[subjects[1]]} />
          <Text variant="h6" fontWeight="bold">
            {subjects[1]}
          </Text>
        </LegendItemContainer>
      </FlexContainer>
      <Spacer y={1} />
      <FlexContainer alignCenter>
        <LegendItemContainer alignCenter>
          <ColoredCircle background={colorCodes[subjects[2]]} />
          <Text variant="h6" fontWeight="bold">
            {subjects[2]}
          </Text>
        </LegendItemContainer>
        <LegendItemContainer alignCenter>
          <ColoredCircle background={colorCodes[subjects[3]]} />
          <Text variant="h6" fontWeight="bold">
            {subjects[3]}
          </Text>
        </LegendItemContainer>
      </FlexContainer>
    </Container>
  );
};

const Container = styled.div``;

const ColoredCircle = styled.div`
  background: ${(props) => props.background};
  height: 30px;
  width: 30px;
  border-radius: 50%;
  margin-right: 1.5rem;
  margin-left: 2.5rem;
  flex-shrink: 0;
  flex-grow: 0;
`;

const LegendItemContainer = styled(FlexContainer)`
  width: 160px;
`;

export default ColorLegend;
