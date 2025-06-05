import { createContext, useContext, ReactNode, useEffect } from "react";
import useRequests from "../hooks/useRequests";
import { isEmpty, isNull } from "lodash";
import { useQueue } from "./QueueContext";
import { useSpotifyScript } from "../hooks/useSpotifyScript";
import { useSpotifyPlayer } from "../hooks/useSpotifyPlayer";
import { useThrottledCallback } from "@mantine/hooks";

interface ContextType {
    loading: boolean;
    currentState: Spotify.PlaybackState | null;
    updateState: () => Promise<void>;
    playNext: () => void;
    playPrevious: () => void;
    playCurrent: () => Promise<any>;
    setVolume: (value: number) => void;
    pause: () => Promise<void>;
    togglePlay: () => Promise<void>;
    resume: () => Promise<void>;
    getVolume: () => Promise<number>;
    seek: (ms: number) => Promise<void>;
}

const PlaybackContext = createContext<ContextType | undefined>(undefined);

export const PlaybackProvider = ({ children }: { children: ReactNode }) => {
    const { queue, current, currentIndex, setCurrentIndex } = useQueue();
    const { player, deviceId, currentState, updateState, loading, error, initiatePlayer } = useSpotifyPlayer();
    const { sendRequest } = useRequests();

    useSpotifyScript(initiatePlayer);

    const transferPlayback = async () =>
        await sendRequest("POST", "spotify/playback/transfer/", {
            body: JSON.stringify({ device_id: deviceId }),
        });

    const playTrack = async (uri: string) => {
        return await sendRequest("POST", "/spotify/playback/start", {
            body: JSON.stringify({ device_id: deviceId, track_uri: uri }),
        });
    };

    useEffect(() => {
        if (!isEmpty(queue) && currentState?.track_window.current_track.uri !== current.uri) {
            playCurrent();
        }
    }, [currentIndex]);

    useEffect(() => {
        transferPlayback();
    }, [deviceId]);

    const playCurrent = async () => await playTrack(current.uri);

    const playNext = () => setCurrentIndex((prev) => (prev === queue.length - 1 ? prev : prev + 1));

    const playPrevious = () => setCurrentIndex((prev) => (prev === 0 ? 0 : prev - 1));

    const setVolume = useThrottledCallback(async (value: number) => await player?.setVolume?.(value), 200);

    if (loading || !player) return null;
    if (error) throw error;

    const togglePlay = async () => {
        if (isNull(queue)) return;
        if (
            isNull(currentState) ||
            (currentState.paused && current.uri !== currentState?.track_window.current_track.uri)
        )
            await playCurrent();
        return await player.togglePlay();
    };

    const pause = async () => {
        if (isNull(currentState)) await transferPlayback();
        return await player.pause();
    };

    const resume = async () => {
        if (isNull(queue)) return;
        if (
            isNull(currentState) ||
            (currentState.paused && current.uri !== currentState?.track_window.current_track.uri)
        )
            await playCurrent();
        return await player.resume();
    };

    const seek = async (ms_pos: number) => {
        await player.seek(ms_pos);
        if (currentState?.paused) await resume();
    };

    const getVolume = async () => await player.getVolume();

    const value = {
        loading,
        currentState,
        updateState,
        playNext,
        playPrevious,
        playCurrent,
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
