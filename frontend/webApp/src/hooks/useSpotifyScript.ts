import { useEffect } from "react";

export const useSpotifyScript = (onReady: () => void) => {
    useEffect(() => {
        const script = document.createElement("script");
        script.src = "https://sdk.scdn.co/spotify-player.js";
        script.async = true;
        document.body.appendChild(script);
        window.onSpotifyWebPlaybackSDKReady = onReady;

        return () => {
            document.body.removeChild(script);
        };
    }, []);
};
