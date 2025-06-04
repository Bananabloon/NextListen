import { createContext, useContext, ReactNode, useState, useEffect } from "react";
import useRequests from "../hooks/useRequests";
import { AppError } from "../utils/errors";
import ERRORS from "../config/errors.config";
import { isNull } from "lodash";

interface ContextType {
    loading: boolean;
    currentState: Spotify.PlaybackState | null;
    updateState: () => Promise<void>;
    nextTrack: () => Promise<void>;
    previousTrack: () => Promise<void>;
    pause: () => Promise<void>;
    togglePlay: () => Promise<void>;
    resume: () => Promise<void>;
    setVolume: (volume: number) => Promise<void>;
    getVolume: () => Promise<number>;
    seek: (ms: number) => Promise<void>;
}

const PlaybackContext = createContext<ContextType | undefined>(undefined);

export const PlaybackProvider = ({ children }: { children: ReactNode }) => {
    const { sendRequest } = useRequests();
    const [player, setPlayer] = useState<Spotify.Player | null>(null);
    const [currentState, setCurrentState] = useState<Spotify.PlaybackState | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | AppError>(null);
    const [deviceId, setDeviceId] = useState<string | null>(null);

    const initiateScript = () => {
        const script = document.createElement("script");
        script.src = "https://sdk.scdn.co/spotify-player.js";
        script.async = true;
        document.body.appendChild(script);
        return script;
    };

    const closeScript = (script: HTMLScriptElement) => {
        document.body.removeChild(script);
    };

    const getToken = async () => {
        const res = await sendRequest("GET", "/spotify/tokens");
        return res.access_token;
    };

    const updateState = async () => await player?.getCurrentState?.()?.then?.((newState) => setCurrentState(newState));

    const initiatePlayer = () => {
        if (player) return;

        const newPlayer: Spotify.Player = new window.Spotify.Player({
            name: "NextListen",
            volume: 0.1,
            getOAuthToken: (callback) => getToken().then(callback),
        });

        newPlayer.addListener("ready", ({ device_id }) => {
            console.log("Ready with Device ID", device_id);
            setDeviceId(device_id);
        });

        newPlayer.addListener("not_ready", ({ device_id }) => {
            console.log("Device ID has gone offline", device_id);
            setDeviceId(null);
        });

        newPlayer.addListener("initialization_error", ({ message }) => {
            console.error(message);
        });

        newPlayer.addListener("authentication_error", ({ message }) => {
            console.error(message);
        });

        newPlayer.addListener("account_error", ({ message }) => {
            setError(new AppError(ERRORS._403_PREMIUM_REQUIRED));
        });

        setPlayer(newPlayer);
    };

    useEffect(() => {
        setLoading(true);
        if (!player) {
            const script = initiateScript();

            window.onSpotifyWebPlaybackSDKReady = initiatePlayer;

            return () => closeScript(script);
        }
    }, []);

    useEffect(() => {
        if (!player) return;

        player.connect();
        setLoading(false);

        const interval = setInterval(updateState, 1000);

        const handleBeforeUnload = () => player.disconnect();
        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            clearInterval(interval);
            player.disconnect();
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [player]);

    if (loading || !player) {
        return null;
    }

    if (error) {
        throw error;
    }

    const { nextTrack, previousTrack, pause, setVolume, getVolume, seek } = player;

    const transferPlayback = async () =>
        await sendRequest("POST", "spotify/playback/transfer/", { body: JSON.stringify({ device_id: deviceId }) });

    const togglePlay = async () => {
        console.log(deviceId);
        if (isNull(currentState)) {
            await transferPlayback();
        }
        return await player.togglePlay();
    };

    const resume = async () => {
        if (isNull(currentState)) {
            await transferPlayback();
        }
        return await player.resume();
    };

    const addToQueue = (uri: string) => {};

    const setQueue = (uris: string[]) => {};

    const playTrack = (uri: string) => {};

    const value = {
        loading,
        currentState,
        updateState,
        nextTrack,
        previousTrack,
        pause,
        togglePlay,
        resume,
        setVolume,
        getVolume,
        seek,
    };

    return <PlaybackContext.Provider value={value}>{children}</PlaybackContext.Provider>;
};

export const usePlayback = () => {
    const context = useContext(PlaybackContext);
    if (!context) throw new Error("usePlayback must be used within a PlaybackProvider");
    return context;
};
