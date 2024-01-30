import useLocalStorage from "./useLocalStorage";

const useHashedId = () => {
  const [hashedId, setHashedId] = useLocalStorage("hashed_id", null);

  return {
    hashedId,
    setHashedId,
  };
};

export default useHashedId;
