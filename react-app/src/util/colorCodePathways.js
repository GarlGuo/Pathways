const colorCodePathways = (pathways) => {
  if (!pathways) return null;

  const colors = [
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#17BECF",
    "#7F7F7F",
    "#BCBD22",
    "#E377C2",
  ];

  let colorIdx = 0;

  const subjectToColor = {
    MISC: "#C4C4C4",
  };

  const colorCodes = [];

  pathways?.forEach((pathway) => {
    const counter = {};
    Object.values(pathway?.courses).forEach((courses) => {
      courses?.forEach((course) => {
        const firstDigitIdx = course?.course_name.search(/\d/);
        const subject = course?.course_name?.substring(0, firstDigitIdx);

        if (!counter.hasOwnProperty(subject)) {
          counter[subject] = 1;
        } else {
          counter[subject] = counter[subject] + 1;
        }
      });
    });

    const subjectCountPairs = [];

    Object.entries(counter).forEach(([key, value]) => {
      subjectCountPairs.push([key, value]);
    });

    subjectCountPairs.sort((a, b) => b[1] - a[1]);

    const topThreeSubjects = subjectCountPairs
      .slice(0, 3)
      .map(([subject]) => subject);

    const pathwayColorCode = {};

    topThreeSubjects?.forEach((subject) => {
      if (!Object.keys(subjectToColor).includes(subject)) {
        // assign color to new subject
        subjectToColor[subject] = colors[colorIdx];
        colorIdx = (colorIdx + 1) % colors.length;
      }
      pathwayColorCode[subject] = subjectToColor[subject];
    });

    pathwayColorCode["MISC"] = subjectToColor["MISC"];
    colorCodes.push(pathwayColorCode);
  });

  return colorCodes;
};

export default colorCodePathways;
