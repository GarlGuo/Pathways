import useLocalStorage from "./useLocalStorage";

const useAuthRedirect = () => {
  const [authRedirect, setAuthRedirect] = useLocalStorage(
    "auth_redirect",
    null
  );

  return {
    authRedirect,
    setAuthRedirect,
  };
};

export default useAuthRedirect;
