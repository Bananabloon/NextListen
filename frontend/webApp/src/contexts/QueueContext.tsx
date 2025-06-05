import { createContext, useContext, ReactNode, useState } from "react";
import { GeneratedSong } from "../types/api.types";
import useRequests from "../hooks/useRequests";

interface QueueContextType {
    queue: GeneratedSong[];
    current: GeneratedSong;
    loading: boolean;
    currentIndex: number;
    setCurrentIndex: (callback: number | ((prev: number) => number)) => void;
    generateDiscoveryFromTop: () => Promise<void>;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

export const QueueProvider = ({ children }: { children: ReactNode }) => {
    const [queue, setQueue] = useState<GeneratedSong[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const { sendRequest } = useRequests();

    const generateDiscoveryFromTop = async () => {
        setLoading(true);
        return sendRequest("POST", "/songs/generate-from-top/", { body: JSON.stringify({ count: 10 }) }).then(
            (data) => {
                setQueue(data?.songs ?? []);
                setLoading(false);
            }
        );
    };

    const current = queue?.[currentIndex] ?? null;

    const value = {
        queue,
        current,
        loading,
        currentIndex,
        setCurrentIndex,
        generateDiscoveryFromTop,
    };

    return <QueueContext.Provider value={value}>{children}</QueueContext.Provider>;
};

export const useQueue = () => {
    const context = useContext(QueueContext);
    if (!context) throw new Error("useQueue must be used within a QueueProvider");
    return context;
};
