import { Popover } from '@mui/material';
import React, { useEffect, useRef, useState } from "react";
import useApi from 'src/hooks/useApi';
import useFullname from 'src/hooks/useFullname';
import useHashedId from 'src/hooks/useHashedId';
import useRouter from 'src/hooks/useRouter';
import styled from 'styled-components';
import Button from '../Button';
import FlexContainer from '../containers/FlexContainer';
import Text from '../Text';
import logo from "./images/logo.svg";
import profile from "./images/profile.svg";

const Nav = () => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const api = useApi()
  const { fullname, setFullname } = useFullname()
  const { hashedId, setHashedId } = useHashedId()
  const router = useRouter()
  const dashboardTutorialAnchorRef = useRef(null)
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const fetchNumberOfDashboardVisits = async () => {
    const res = await api.post('/get_number_of_dashboard_visits', {
      hashed_id: hashedId
    })
    setIsTutorialOpen(res?.data?.number_of_dashboard_visits === 0 && router?.location?.pathname !== '/dashboard')
  }

  const handleCloseTutorial = () => {
    setIsTutorialOpen(false)
  }

  useEffect(() => {
    fetchNumberOfDashboardVisits()
  }, [])

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  const handleSignout = () => {
    setHashedId(null)
    setFullname(null)
    router.push('/')
  }

  return (
    <NavContainer alignCenter justifySpaceBetween>
      <FlexContainer alignCenter>
        <Link href="/">
          <img src={logo} alt='Pathways logo' />
        </Link>
        <DashboardButtonContainer ref={dashboardTutorialAnchorRef}>
          <Link href='/dashboard'>
            <NavButton>
              Dashboard
            </NavButton>
          </Link>
          <TutorialPopover
            id={id}
            open={isTutorialOpen}
            anchorEl={dashboardTutorialAnchorRef?.current}
            onClose={handleCloseTutorial}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <TutorialContainer>
              <TutorialTitle>Dashboard</TutorialTitle>
              <Text variant='meta1'>We have a new feature! You can now save classes, pathways, and view your search history in Dashboard here.</Text>
            </TutorialContainer>
          </TutorialPopover>
          {isTutorialOpen && <Overlay />}
        </DashboardButtonContainer>
      </FlexContainer>
      <Profile src={profile} alt='User profile' onClick={handleClick} />
      <StyledPopover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <PopoverContainer>
          <Name>{fullname}</Name>
          <Button variant='subtle' onClick={handleSignout}>Sign out</Button>
        </PopoverContainer>
      </StyledPopover>
    </NavContainer>
  );
};

const NavContainer = styled(FlexContainer)`
  background: #4F42B5;
  height: 50px;
  padding-left: 1rem;

  & > * {
    margin: 0 .5rem;
  }
`;

const DashboardButtonContainer = styled.div`
  position: relative;
`;

const NavButton = styled.button`
  color: #ffffff;
  background: inherit;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  letter-spacing: .05rem;
`;

const Link = styled.a`
  display: inline-block;
`;

const Profile = styled.img`
  margin-right: 1.5rem;
  cursor: pointer;
`;

const StyledPopover = styled(Popover)`
  margin-top: .7rem;
`;

const TutorialPopover = styled(Popover)`
  margin-left: 8rem;
  margin-top: .3rem;
`;

const PopoverContainer = styled.div`
  padding: 1rem .5rem;
  min-width: 10rem;
`;

const TutorialContainer = styled.div`
  width: 300px;
  padding: 1rem 1rem;
`;

const TutorialTitle = styled(Text)`
  font-weight: 700;
  margin-bottom: .3rem;
`;

const Name = styled.p`
  margin: 0;
  margin-left: .7rem;
  margin-bottom: .2rem;
  font-weight: 700;
`;

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, .2);
`;

export default Nav;
