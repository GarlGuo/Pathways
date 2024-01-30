import useHashedId from "src/hooks/useHashedId";
import useRouter from "src/hooks/useRouter";
import Button from "../Button";
import logo from "./images/logo.svg";
import "./LandingHeader.css";

const LandingHeader = () => {
  const { hashedId, setHashedId } = useHashedId();
  const router = useRouter();

  const handleSignOut = () => {
    router.push("/");
    setHashedId(null);
  };

  const handleSignIn = async () => {
    router.push("/search");
  };

  return (
    <div className="header">
      <div className="header-left">
        <a href="/">
          {" "}
          <img src={logo} width="180px" alt="Pathways" />
        </a>
        <a href="/team" style={{ marginLeft: 49 }}>
          Team
        </a>
        <a href="/research" style={{ marginLeft: 49 }}>
          Research
        </a>
      </div>

      {/* {hashedId ? (
        <Button onClick={handleSignOut}>Sign out</Button>
      ) : (
        <Button onClick={handleSignIn}>Sign in</Button>
      )} */}
    </div>
  );
};

export default LandingHeader;
