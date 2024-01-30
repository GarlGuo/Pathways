import Button from 'src/components/Button';
import exportImg from "src/assets/images/download_icon.png"
import styled from 'styled-components';

const ExportPathwayButton = ({ searchId, visualizationPositionIndex, data, colorCodes, setExportData,...rest }) =>{
    const {minors, majors, courses,pathway_id,career_outcome}=data
    const colorCodedCourses = {}

    Object.entries(courses)?.forEach(([key, semesterCourses]) => {
      colorCodedCourses[key] = semesterCourses?.map((course) => {
          const firstDigitIdx = course?.course_name.search(/\d/);
          const subject = course?.course_name?.substring(0, firstDigitIdx);
          let subjectForColor = 'MISC'
          if (subject in colorCodes) subjectForColor = subject
          return {
            ...course,
            color: colorCodes[subjectForColor]
          }
      })
    })

    const onClickHandler= async ()=>{

    let sentData={
        searchId,
        courses,
        majors,
        minors,
        career_outcome,
        pathway_id
      }
      setExportData(sentData)
}
    return <Button onClick={onClickHandler} leftIcon variant='outlined' {...rest}>
      <ExportImg src={exportImg}/>
      Download as Image
    </Button>
}

export default ExportPathwayButton;

const ExportImg = styled.img`
  height: 17px;
  width: 17px;
`;