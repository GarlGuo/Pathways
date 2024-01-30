import React, { useEffect } from "react";
import Nav from "../../components/Nav";
import "./Dashboard.css";
import WelcomeBar from "./components/WelcomeBar";
import TableFrame from "./components/TableFrame";
import useApi from 'src/hooks/useApi';
import useHashedId from 'src/hooks/useHashedId';

const Dashboard = () => {
  const api = useApi()
  const { hashedId } = useHashedId()

  const handleVisitDashboard =  () => {
    api.post('/visit_dashboard', {
      hashed_id: hashedId
    })
  }

  useEffect(() => {
    handleVisitDashboard()
  }, [])

  return (
    <div>
      <Nav></Nav>
      <WelcomeBar></WelcomeBar>
      <TableFrame></TableFrame>
    </div>
  );
};

export default Dashboard;
