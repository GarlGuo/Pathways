import Visualization from "./Visualization";

const VisualizationDemo = () => {
  return (
    <div>
      <Visualization
        is_major_declared={true}
        majors={[]}
        searchId={1}
        searched={true}
        interest_keywords={[""]}
        suggested_courses={[]}
        otherMajor={[]}
      />
    </div>
  );
};

export default VisualizationDemo;
