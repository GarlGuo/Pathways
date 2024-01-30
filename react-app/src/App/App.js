import { MantineProvider } from '@mantine/core';
import { NotificationsProvider } from '@mantine/notifications';
import { BrowserRouter as Router, Route } from "react-router-dom";
import AuthWrapper from 'src/components/AuthWrapper';
import FeedbackModalButton from 'src/components/FeedbackModalButton';
import VisualizationDemo from "src/screens/Visualization/VisualizationDemo";
import Dashboard from "../screens/Dashboard";
import Landing from "../screens/Landing";
import Research from "../screens/Research/Research";
import Search from "../screens/Search";
import Team from "../screens/Team";
import "./App.css";

const App = () => {

  return (
    <MantineProvider withGlobalStyles>
      <NotificationsProvider>
        <Router>
          <AuthWrapper>
            <FeedbackModalButton />
            <Route path="/dashboard" component={Dashboard} />
            <Route path="/visualization" component={VisualizationDemo} />
            <Route path="/search" component={Search} />
            <Route path="/team" component={Team} />
            <Route path="/research" component={Research} />
            <Route exact path="/" component={Landing} />
          </AuthWrapper>
        </Router>
      </NotificationsProvider>
    </MantineProvider>
  );
};

export default App;
