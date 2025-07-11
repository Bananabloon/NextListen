import { createContext, useContext, ReactNode, useState, useEffect } from "react";
import { DiscoveryOptionsMap, DiscoveryState, DiscoveryType, GeneratedSong } from "../types/api.types";
import useRequests from "../hooks/useRequests";
import { isArray, isEmpty, isNull, isNumber, isUndefined, max } from "lodash";
import { prominent } from "color.js";
import { hexToRgb } from "../utils/colors";

interface QueueContextType {
    queue: GeneratedSong[];
    current: GeneratedSong;
    loading: boolean;
    currentColor: string;
    currentIndex: number;
    setCurrentIndex: (callback: number | ((prev: number) => number)) => void;
    createNewDiscoveryQueue: <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => Promise<void>;
    restoreDiscoveryQueue: <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => Promise<void>;
}

interface sessionQueueData {
    queue: GeneratedSong[];
    index: number;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

const API_PATHS: Record<DiscoveryType, string> = {
    top: "/songs/generate-from-top/",
    tracks: "/songs/generate-from-song/",
    artists: "/songs/generate-from-artist/",
    genres: "/songs/generate-from-genre/",
};

export const QueueProvider = ({ children }: { children: ReactNode }) => {
    const [queue, setQueue] = useState<GeneratedSong[]>([]);
    const [currentIndex, setCurrentIndex] = useState(-1);
    const [currentColor, setCurrentColor] = useState("var(--primary-color)");
    const [loading, setLoading] = useState(false);
    const [updating, setUpdating] = useState(false);
    const [discoveryState, setDiscoveryState] = useState<DiscoveryState>(null);
    const { sendRequest } = useRequests();

    let block = false; // block double fetches in the dev mode

    const current = queue?.[currentIndex] ?? null;

    useEffect(() => {
        if (queue.length > 0) {
            sessionStorage.setItem("queue", JSON.stringify(queue));
        }
        if (currentIndex !== -1) {
            sessionStorage.setItem("currentIndex", JSON.stringify(currentIndex));
        }
    }, [queue, currentIndex]);

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

    const parseStorage = (): sessionQueueData | undefined => {
        const storedQueue = sessionStorage.getItem("queue");
        const storedIndex = sessionStorage.getItem("currentIndex") || "0"; //set to 0 to prevent generation of a new queue when storedIndex isn't available
        if (!storedQueue) return;

        try {
            const parsedQueue: GeneratedSong[] = JSON.parse(storedQueue);
            const parsedIndex: number = JSON.parse(storedIndex);

            if (!isArray(parsedQueue) || isEmpty(parsedQueue)) return;
            return { queue: parsedQueue, index: isNumber(parsedIndex) ? parsedIndex : 0 };
        } catch (err) {
            console.error("Couldn't parse queue or index from the session storage.");
        }
    };

    const restoreDiscoveryQueue = async <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => {
        if ((!isEmpty(queue) && isArray(queue)) || loading || block) return;

        block = true;
        setLoading(true);
        const cachedItems = parseStorage();
        const [cachedQueue, cachedIndex] = [cachedItems?.queue, cachedItems?.index];
        if (cachedQueue && !isUndefined(cachedIndex)) {
            setQueue(cachedQueue);
            setCurrentIndex(cachedIndex);
        } else {
            setQueue(await generateDiscovery(type, options));
            setCurrentIndex(0);
        }
        setDiscoveryState({ type, options } as DiscoveryState);
        setLoading(false);
        block = false;
    };

    const createNewDiscoveryQueue = async <T extends DiscoveryType>(type: T, options: DiscoveryOptionsMap[T]) => {
        if (loading || block) return;
        block = true;
        setLoading(true);
        setQueue(await generateDiscovery(type, options));
        setDiscoveryState({ type, options } as DiscoveryState);
        setLoading(false);
        setCurrentIndex(0);
        updateCurrentColor();
        block = false;
    };

    const updateCurrentColor = async () => {
        if (!current) return;
        const colors = (await prominent(current?.track_details?.album_cover, { amount: 20, format: "hex", group: 50 })) as string[];
        const aliveColor =
            colors.find((color) => {
                const rgb = hexToRgb(color);
                return (max(rgb) ?? 0) >= 134;
            }) ?? "var(--primary-color-7)";
        setCurrentColor(current.curveball ? "var(--primary-color-7)" : aliveColor);
    };

    useEffect(() => {
        updateDiscoveryQueue();
        updateCurrentColor();
    }, [currentIndex]);

    const value = {
        queue,
        current,
        loading,
        currentColor,
        currentIndex,
        setCurrentIndex,
        createNewDiscoveryQueue,
        restoreDiscoveryQueue,
    };

    return <QueueContext.Provider value={value}>{children}</QueueContext.Provider>;
};

export const useQueue = () => {
    const context = useContext(QueueContext);
    if (!context) throw new Error("useQueue must be used within a QueueProvider");
    return context;
};
