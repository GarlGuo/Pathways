import useLocalStorage from "./useLocalStorage";

const useAuthExpire = () => {
  const [authExpire, setAuthExpire] = useLocalStorage("auth-expire", null);

  return {
    authExpire,
    setAuthExpire,
  };
};

export default useAuthExpire;
