import loopIcon from "../assets/loop.png";

const Courses = ({
  courses,
  selectedCourses,
  setSelectedCourses,
  disabled,
  loadCourseBatch,
}) => {
  return (
    <div
      className={
        disabled ? "question-container disabled" : "question-container"
      }
    >
      <p style={{ fontSize: 18 }}>
        Take a look at these courses taken by students who share some of your interests. Which of these courses spur your interests? Selecting them below helps us better calibrate the following results.
      </p>
      <div className="courses-grid">
        {courses?.map((course) => (
          <div
            className={
              selectedCourses.includes(course)
                ? "course course-selected"
                : "course"
            }
            onClick={() => {
              if (!disabled) {
                if (!selectedCourses.includes(course)) {
                  setSelectedCourses((courses) => [...courses, course]);
                } else {
                  setSelectedCourses((courses) =>
                    courses.filter((c) => c != course)
                  );
                }
              }
            }}
          >
            <span style={{ fontSize: 18 }}>{course.course_name}</span>
            <div style={{ fontSize: 18 }}>{course.course_title}</div>
          </div>
        ))}
      </div>
      <div style={{ textAlign: "right" }}>
        <span
          className="load-text"
          style={
            disabled ? { display: "inline-block", marginTop: 10, cursor: "default" } : { display: "inline-block", marginTop: 10 }
          }
          onClick={disabled ? null : loadCourseBatch}
        >
          Load another batch
          <img className="loop" src={loopIcon} alt="Loop" />
        </span>
      </div>
    </div>
  );
};

export default Courses;
