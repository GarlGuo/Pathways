import React, {useState} from "react";
import SavedClasses from "../SavedClasses";
import SavedPathways from "../SavedPathways";
import SearchHistory from "../SearchHistory";
import styled from 'styled-components'
import "./TableFrame.css";

const Tab = ({ tab, children, currentTab, onClick }) =>
    <div
        className={`tab ${currentTab === tab && 'active-tab'}`}
        onClick={onClick}
    >{children}</div>;

const TableFrame = () => {
    const [currentTab, setCurrentTab] = useState("savedPathways");
    return (
        <TableCard>
            <div id="tabs">
                <Tab
                    tab="savedPathways"
                    currentTab={currentTab}
                    onClick={() => setCurrentTab("savedPathways")}
                >Saved Pathways</Tab>
                <Tab
                    tab="savedClasses"
                    currentTab={currentTab}
                    onClick={() => setCurrentTab("savedClasses")}
                >Saved Classes</Tab>
                <Tab
                    tab="searchHistory"
                    currentTab={currentTab}
                    onClick={() => setCurrentTab("searchHistory")}
                >Search History</Tab>
            </div>
            <Content>
                {currentTab === "savedClasses" && <SavedClasses></SavedClasses>}
                {currentTab === "savedPathways" && <SavedPathways></SavedPathways>}
                {currentTab === "searchHistory" && <SearchHistory></SearchHistory>}
            </Content>
        </TableCard>
    );
};

const TableCard = styled.div`
    background-color: white;
    border: 1px solid rgba(0, 0, 0, .05);
    box-shadow: 5px 10px 20px rgba(41, 95, 171, 0.05);
    border-radius: 10px;
    margin: 30px;
    padding: 20px 30px;
`;

const Content = styled.div`
    margin-top: 24px;
`;

export default TableFrame;
