import { useEffect } from 'react';
import useApi from './useApi';
import useHashedId from './useHashedId';
import useLocalStorage from "./useLocalStorage";

const useFullname = () => {
  const { hashedId } = useHashedId()
  const api = useApi()
  const [fullname, setFullname] = useLocalStorage("full_name", null);

  const fetchFullname = async () => {
    const { data } = await api.post('/get_user_full_name', {
      hashed_id: hashedId
    })

    setFullname(data?.full_name)
  }

  useEffect(() => {
    if (hashedId && !fullname) {
      fetchFullname()
    }
  }, [fullname, hashedId])

  return {
    fullname,
    setFullname,
  };
};

export default useFullname;
