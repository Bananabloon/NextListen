import { createContext, useContext, ReactNode, useState, useEffect } from "react";
import { DiscoveryOptionsMap, DiscoveryState, DiscoveryType, GeneratedSong } from "../types/api.types";
import useRequests from "../hooks/useRequests";
import { isEmpty, isNull } from "lodash";

interface QueueContextType {
    queue: GeneratedSong[];
    current: GeneratedSong;
    loading: boolean;
    currentIndex: number;
    setCurrentIndex: (callback: number | ((prev: number) => number)) => void;
    createNewDiscoveryQueue: <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => Promise<void>;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

const API_PATHS: Record<DiscoveryType, string> = {
    top: "/songs/generate-from-top/",
    song: "/songs/generate-from-song/",
    artist: "/songs/generate-from-artist/",
    genre: "/songs/generate-from-genre/",
};

export const QueueProvider = ({ children }: { children: ReactNode }) => {
    const [queue, setQueue] = useState<GeneratedSong[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const [updating, setUpdating] = useState(false);
    const [discoveryState, setDiscoveryState] = useState<DiscoveryState>(null);
    const { sendRequest } = useRequests();

    const current = queue?.[currentIndex] ?? null;

    const generateDiscovery = async <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => {
        const data = await sendRequest("POST", API_PATHS[type], { body: JSON.stringify(options) });
        return data?.songs ?? [];
    };

    const updateDiscoveryQueue = async () => {
        if (isEmpty(queue) || isNull(discoveryState) || loading || updating || currentIndex + 10 >= queue.length) return;

        setUpdating(true);
        const songs = await generateDiscovery(discoveryState.type, discoveryState.options);
        setQueue((prev) => [...prev, ...songs]);
        setUpdating(false);
    };

    const createNewDiscoveryQueue = async <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => {
        console.log(type);
        setLoading(true);
        setQueue(await generateDiscovery(type, options));
        setDiscoveryState({ type, options } as DiscoveryState);
        setLoading(false);
    };

    useEffect(() => {
        updateDiscoveryQueue();
    }, [currentIndex]);

    const value = {
        queue,
        current,
        loading,
        currentIndex,
        setCurrentIndex,
        createNewDiscoveryQueue,
    };

    return <QueueContext.Provider value={value}>{children}</QueueContext.Provider>;
};

export const useQueue = () => {
    const context = useContext(QueueContext);
    if (!context) throw new Error("useQueue must be used within a QueueProvider");
    return context;
};
