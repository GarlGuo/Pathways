import axios from "axios";
import useHashedId from "./useHashedId";
import { showNotification } from '@mantine/notifications';

const useApi = () => {
  const api = axios.create();
  const { hashedId } = useHashedId();

  api.interceptors.response.use((response) => {
    return response;
  }, (error) => {
    if (process.env.NODE_ENV === "production") {
      showNotification({
        title: 'Oops!',
        message: 'An error has occured. The team has been notified and will fix this error soon.',
        color: 'red'
      })
    } else {
      return Promise.reject(error);
    }
  });

  api.interceptors.request.use(
    async (req) => {
      if (!hashedId) {
        const endpoint =
          process.env.NODE_ENV === "production" ? "/api/auth/sso" : "/auth/sso";
        const { data } = await axios.post(endpoint);
        window.location.replace(data["url"]);
      } else {
        return req;
      }
    },
    (error) => {
      if (process.env.NODE_ENV === "production") {
        showNotification({
          title: 'Oops!',
          message: 'An error has occured. The team has been notified and will fix this error soon.',
          color: 'red'
        })
      } else {
        return Promise.reject(error);
      }
    }
  );

  if (process.env.NODE_ENV === "production") {
    api.defaults.baseURL = "https://pathways.cornell.edu/api/";
  }

  return api;
};

export default useApi;
