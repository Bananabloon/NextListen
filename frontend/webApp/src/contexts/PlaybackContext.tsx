import { createContext, useContext, ReactNode } from "react";
import useRequests from "../hooks/useRequests";

interface ContextType {}

const PlaybackContext = createContext<ContextType | undefined>(undefined);

export const PlaybackProvider = ({ children }: { children: ReactNode }) => {
    const { sendRequest } = useRequests();

    const getToken = () => {};

    const value = {};

    return <PlaybackContext.Provider value={value}>{children}</PlaybackContext.Provider>;
};

export const usePlayback = () => {
    const context = useContext(PlaybackContext);
    if (!context) throw new Error("usePlayback must be used within a PlaybackProvider");
    return context;
};
