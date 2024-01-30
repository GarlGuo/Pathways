import { useEffect, useRef } from "react";
// See: https://usehooks-ts.com/react-hook/use-isomorphic-layout-effect
import useIsomorphicLayoutEffect from "./useIsomorphicLayoutEffect";

function useEventListener(eventName, handler, element) {
  // Create a ref that stores handler
  const savedHandler = useRef(handler);
  useIsomorphicLayoutEffect(() => {
    savedHandler.current = handler;
  }, [handler]);
  useEffect(() => {
    // Define the listening target
    const targetElement =
      (element === null || element === void 0 ? void 0 : element.current) ||
      window;
    if (!(targetElement && targetElement.addEventListener)) {
      return;
    }
    // Create event listener that calls handler function stored in ref
    const eventListener = (event) => savedHandler.current(event);
    targetElement.addEventListener(eventName, eventListener);
    // Remove event listener on cleanup
    return () => {
      targetElement.removeEventListener(eventName, eventListener);
    };
  }, [eventName, element]);
}

export default useEventListener;
