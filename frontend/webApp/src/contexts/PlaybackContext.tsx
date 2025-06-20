import { createContext, useContext, ReactNode, useEffect } from "react";
import useRequests from "../hooks/useRequests";
import { isEmpty, isNull } from "lodash";
import { useQueue } from "./QueueContext";
import { useSpotifyScript } from "../hooks/useSpotifyScript";
import { useSpotifyPlayer } from "../hooks/useSpotifyPlayer";
import { useDebouncedCallback, useThrottledCallback } from "@mantine/hooks";

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
    const { queue, current, currentIndex, setCurrentIndex, loading: queueLoading } = useQueue();
    const { player, deviceId, currentState, updateState, loading, error, initiatePlayer } = useSpotifyPlayer();
    const { sendRequest } = useRequests();

    useSpotifyScript(initiatePlayer);

    const transferPlayback = async () =>
        await sendRequest("POST", "spotify/playback/transfer/", {
            body: JSON.stringify({ device_id: deviceId }),
        });

    const playTrack = useDebouncedCallback(async (uri: string) => {
        return await sendRequest("POST", "/spotify/playback/start", {
            body: JSON.stringify({ device_id: deviceId, track_uri: uri }),
        });
    }, 500);

    const playCurrent = async () => await playTrack(current.uri);

    // playNext and playPrevious just update the index, useEffect bellow handles the rest
    const playNext = useThrottledCallback(() => setCurrentIndex((prev) => (prev === queue.length - 1 ? prev : prev + 1)), 600);

    const playPrevious = useThrottledCallback(() => setCurrentIndex((prev) => (prev === 0 ? 0 : prev - 1)), 600);

    // if currentIndex changed, update the track that is being played
    useEffect(() => {
        if (!isEmpty(queue) && currentState?.track_window.current_track.uri !== current?.uri) {
            playCurrent();
        }
    }, [currentIndex]);

    useEffect(() => {
        if (deviceId) transferPlayback();
    }, [deviceId]);

    // currentState gets updated every second, so this check will match exactly once at the end of the track
    useEffect(() => {
        if (!isEmpty(currentState) && currentState.duration - currentState.position <= 1000) {
            playNext();
        }
    }, [currentState?.timestamp]);

    useEffect(() => {
        player?.seek(0);
        player?.pause();
    }, [queueLoading]);

    // volume value was way too high so it's divided by 5
    const setVolume = useThrottledCallback(async (value: number) => await player?.setVolume?.(value / 5), 200);

    if (loading || !player) return null;
    if (error) throw error;

    const shouldUpdateCurrentTrack = () =>
        isNull(currentState) || (currentState.paused && current.uri !== currentState?.track_window.current_track.uri);

    const togglePlay = async () => {
        if (isNull(queue)) return;
        if (shouldUpdateCurrentTrack()) return await playCurrent();
        return await player.togglePlay();
    };

    const pause = async () => {
        if (isNull(currentState)) await transferPlayback();
        return await player.pause();
    };

    const resume = async () => {
        if (isNull(queue)) return;
        if (shouldUpdateCurrentTrack()) return await playCurrent();
        return await player.togglePlay();
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
