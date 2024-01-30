import majorsData from "../data/majorsData.json";
import Select from "react-select";
import { useState, useEffect } from "react";

const SelectMajor = ({ declaredMajor, majors, setMajors, otherMajor, setOtherMajor, disabled }) => {
  const [majorOptions, setMajorOptions] = useState(majorsData);

  useEffect(() => {
    if (declaredMajor) {
      setMajorOptions(majorsData.filter(m => m.value !== "Undecided")); // REMOVE "UNDECIDED" IF MAJOR IS DECLARED
    } else {
      if (majors.length > 0) {
        setMajorOptions(majorsData.filter(m => m.value !== "Undecided")); // REMOVE "UNDECIDED" IF MAJOR IS ALREADY SELECTED
      } else {
        setMajorOptions(majorsData); // RE-ADD "UNDECIDED"
      }
    }
  }, [declaredMajor])

  const handleChange = (data) => {
    const majorsData = data.map(m => m.value)

    if (!majorsData.includes("Other")) {
      setOtherMajor("");
    }

    setMajors(majorsData);
  }

  return (
    <div className={disabled ? "question-container disabled" : "question-container"}>
      <h3 style={{ fontSize: 18 }}>{declaredMajor ? "What major(s) have you declared?" : "What major(s) are you interested in?"}</h3>
      <p style={{ fontSize: 18, marginVertical: 15 }}>{declaredMajor ? 'If you are thinking about adding or changing your major(s), write down the major(s) you are interested in.' : 'If you don’t have an intended major yet, no worries, that’s why we are here! You can simply select “undecided” as a major or try out different intended majors in the search.'}</p>
      <div>
        <Select
          isMulti
          className="react-select"
          options={majorOptions}
          value={majors?.map((major) => ({
            label: major,
            value: major
          }))}
          onChange={handleChange}
          isDisabled={disabled}
          isOptionDisabled={(option) => majors.includes("Undecided")}
        />
        {majors.includes("Other") ?
          <div style={{ marginTop: 15 }}>
            <input
              className="input"
              type="text"
              placeholder="Type in your major"
              value={otherMajor}
              onChange={(e) => setOtherMajor(e.target.value)}
            />
          </div> : <></>
        }
      </div>
    </div>
  )
}

export default SelectMajor;
