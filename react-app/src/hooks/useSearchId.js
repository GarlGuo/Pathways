import useLocalStorage from "./useLocalStorage";

const useSearchId = () => {
  const [searchId, setSearchId] = useLocalStorage("search_id", null);

  return {
    searchId,
    setSearchId,
  };
};

export default useSearchId;
