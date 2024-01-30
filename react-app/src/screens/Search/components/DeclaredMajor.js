const DeclaredMajor = ({ declaredMajor, setDeclaredMajor, disabled }) => {
  return (
    <div className={disabled ? "question-container disabled" : "question-container"}>
      <h3 style={{ fontSize: 18 }}>Have you already declared a major? <span style={{ color: "red" }}>*</span></h3>
      <div>
        <label style={{ fontSize: 17 }}>
          <input
            type="radio"
            name="declared-major"
            checked={declaredMajor}
            onClick={() => setDeclaredMajor(true)}
            disabled={disabled}
          />
          <span style={{ marginLeft: 5 }}>Yes</span>
        </label>
      </div>
      <div style={{ marginTop: 3 }}>
        <label style={{ fontSize: 17 }}>
          <input
            type="radio"
            name="declared-major"
            checked={declaredMajor === false}
            onClick={() => setDeclaredMajor(false)}
            disabled={disabled}
          />
          <span style={{ marginLeft: 5 }}>No</span>
        </label>
      </div>
    </div>
  )
}

export default DeclaredMajor;
