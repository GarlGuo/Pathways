/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { useState } from "react";
import loopIcon from "../assets/loop.png";
import xIcon from "../assets/x.png";

const Interests = ({ interests, setInterests, disabled }) => {
  const [interestText, setInterestText] = useState("");

  const addInterest = (e) => {
    e.preventDefault();
    if (interestText) {
      setInterests(interests => [ ...interests, interestText ]);
      setInterestText("");
    }
  }

  return (
    <div className={disabled ? "question-container disabled" : "question-container"}>
      <h3 style={{ fontSize: 18 }}>Finally, take a few minutes to share what topics you are interested in learning about. <span style={{ color: "red" }}>*</span></h3>
      <p style={{ fontSize: 18 }}>Add keywords for <strong>ANY</strong> topic below! We encourage you to explore more than one interest. Exploring and finding interests is one of the most important experiences in college. It is motivating and helps you enjoy and excel in your classes. For inspiration, you can think back to any classes, clubs, events, or news articles that sparked your curiosity.</p>
      <div>
        <div>
          <input
            className="input"
            type="text"
            style={{ fontSize: 18 }}
            placeholder="Type keywords and press Enter"
            value={interestText}
            onChange={(e) => setInterestText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter") addInterest(e);
            }}
            disabled={disabled}
          />
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (!disabled) {
                addInterest(e)
              }
            }}
            style={disabled ? { paddingLeft: 25, fontSize: 18, cursor: "default" } : { paddingLeft: 25 }}
          >Add to the List</a>
        </div>
        <div className="interest-tags">
          {interests.map((interest) => (
            <span className="interest-tag">
              <span className="interest-tag-text" style={{ fontSize: 18 }}>{interest}</span>
              <img
                className="x"
                src={xIcon} alt="x"
                onClick={() => {
                  if (!disabled) {
                    setInterests(interests => interests.filter(i => i != interest));
                  }
                }}
                style={disabled ? { cursor: "default" } : {}}
              />
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Interests;