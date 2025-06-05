import { useState, useEffect, useRef } from "react";
import { AppError } from "../utils/errors";
import ERRORS from "../config/errors.config";
import useRequests from "../hooks/useRequests";

export const useSpotifyPlayer = () => {
    const { sendRequest } = useRequests();
    const [player, setPlayer] = useState<Spotify.Player | null>(null);
    const [deviceId, setDeviceId] = useState<string | null>(null);
    const [error, setError] = useState<null | AppError>(null);
    const [currentState, setCurrentState] = useState<Spotify.PlaybackState | null>(null);
    const [loading, setLoading] = useState(false);
    const playerInitializedRef = useRef(false);

    const getToken = async () => {
        const res = await sendRequest("GET", "/spotify/tokens");
        return res.access_token;
    };

    const updateState = async () => {
        if (!player) return;
        const newState = await player.getCurrentState();
        if (newState) setCurrentState(newState);
    };

    const initiatePlayer = () => {
        if (playerInitializedRef.current) return;

        playerInitializedRef.current = true;

        setLoading(true);
        if (player) return;

        const newPlayer: Spotify.Player = new window.Spotify.Player({
            name: "NextListen",
            volume: 0.1,
            getOAuthToken: (cb) => getToken().then(cb),
        });

        newPlayer.addListener("ready", ({ device_id }) => setDeviceId(device_id));
        newPlayer.addListener("not_ready", () => setDeviceId(null));
        newPlayer.addListener("account_error", () => setError(new AppError(ERRORS._403_PREMIUM_REQUIRED)));
        newPlayer.addListener("initialization_error", (error) => console.error(error));
        newPlayer.addListener("authentication_error", (error) => console.error(error));

        setPlayer(newPlayer);
    };

    useEffect(() => {
        if (!player) return;

        let interval: number;
        player.connect().then((success) => {
            if (!success) return;
            interval = setInterval(updateState, 1000);
            setLoading(false);
        });

        const handleBeforeUnload = () => {
            player.pause();
            player.disconnect();
        };

        window.addEventListener("beforeunload", handleBeforeUnload);
        return () => {
            clearInterval(interval);
            handleBeforeUnload();
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [player]);

    return { player, setPlayer, deviceId, currentState, updateState, error, loading, initiatePlayer };
};
