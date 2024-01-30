import { useEffect } from 'react';
import useAuthExpire from 'src/hooks/useAuthExpire';
import useFullname from 'src/hooks/useFullname';
import useHashedId from 'src/hooks/useHashedId';
import useRouter from 'src/hooks/useRouter';

const AuthWrapper = ({ children }) => {
  const router = useRouter();
  const { hashedId, setHashedId } = useHashedId();
  const { authExpire, setAuthExpire } = useAuthExpire();
  const { setFullname } = useFullname()

  useEffect(() => {
    if (hashedId && (!authExpire || new Date().getTime() > new Date(authExpire).getTime())) {
      // auth expired, automatically sign out
      setHashedId(null)
      setFullname(null)
      setAuthExpire(null)
      router.push('/')
    }
  }, [])

  return (
    <>
      {children}
    </>
  )
}

export default AuthWrapper
