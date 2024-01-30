import React from "react";
import Button from 'src/components/Button';
import FlexContainer from 'src/components/containers/FlexContainer';
import Spacer from 'src/components/Spacer';
import styled from 'styled-components'
import "./WelcomeBar.css";

const WelcomeBar = () => {
    return (
        <Container>
            <FlexContainer align='center'>
                <h1 id="welcome-text">
                    {/* <span>Welcome back,</span> */}
                    Dashboard
                </h1>
                <Spacer x={2} />
                <a href='/search'>
                    <Button>Start a new search </Button>
                </a>
            </FlexContainer>
        </Container>
    );
};

const Container = styled.div`
  padding-left: 2rem;
  padding-top: 3rem;
`;

export default WelcomeBar;
