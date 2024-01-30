import React, { useState } from "react";
import "./TableRow.css";
import removeSvg from "./images/remove.svg";
import dropdownSvg from "./images/dropdown.svg";

const TableRow = ({ first, second, third, onRemove, isDropdown }) => {
  const [hovering, setHovering] = useState(false);
  const [showingDropdown, setShowingDropdown] = useState(false);

  return (
    <tr
      className={showingDropdown ? "expanded" : ""}
      style={{ backgroundColor: hovering || showingDropdown ? "#FFEDC1" : "" }}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <td>
        {(hovering || showingDropdown) && isDropdown && (
          <div
            onClick={() => setShowingDropdown(!showingDropdown)}
            className={
              "dropdown-icon" + (showingDropdown ? " dropdown-icon-active" : "")
            }
          >
            <img src={dropdownSvg} alt="dropdown button" />
          </div>
        )}
      </td>
      <td>{first}</td>
      <td>{second}</td>
      <td>{third}</td>
      <td>
        {(hovering || showingDropdown) && onRemove && (
          <img
            src={removeSvg}
            className="remove-button"
            alt="remove table row button"
          />
        )}
      </td>
      {/* <div className={"more" + (showingDropdown ? " showing" : "")}>Hi there! :)</div> */}
    </tr>
  );
};

export default TableRow;
