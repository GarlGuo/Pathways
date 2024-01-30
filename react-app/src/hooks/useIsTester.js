import useFullname from './useFullname';

const useIsTester = () => {
  const { fullname } = useFullname()
  const testers = ['Jaehyung Joo', 'Mina Chen', 'Sofia (Hee Won) Yoon', 'Wentao Guo', 'Jinsook Lee', 'Rene Kizilcec', 'Ed Dormady', 'John Udall']
  return testers.includes(fullname)
};

export default useIsTester;
