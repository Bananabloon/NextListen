import { useEffect, useState } from "react";
import { useQueue } from "../../../contexts/QueueContext";
import useRequests from "../../../hooks/useRequests";
import { ButtonProps } from "../../atoms/Button/Button";
import IconButton from "../../atoms/IconButton/IconButton";

interface SaveOnSpotifyButtonProps extends ButtonProps {}

const SaveOnSpotifyButton = ({ ...props }: SaveOnSpotifyButtonProps): React.JSX.Element => {
    const [isSaved, setIsSaved] = useState(false);
    const { current } = useQueue();
    const { sendRequest } = useRequests();

    const updateIsSaved = async () => {
        return await sendRequest("GET", `/spotify/are-saved?uris=${current.uri}`).then((data) => setIsSaved(data[current.uri]));
    };

    const save = async () => {
        return await sendRequest("POST", `/spotify/saved-tracks/save`, { body: JSON.stringify({ track_uri: current.uri }) });
    };

    const unsave = async () => {
        return await sendRequest("POST", `/spotify/saved-tracks/remove`, { body: JSON.stringify({ track_uri: current.uri }) });
    };

    useEffect(() => {
        if (current?.uri) updateIsSaved();
    }, [current?.uri]);

    const toggleSaved = () => {
        if (!current.uri) return;
        setIsSaved((prev) => {
            prev ? unsave() : save();
            return !prev;
        });
    };

    return (
        <IconButton
            size="md"
            {...props}
            variant="transparent"
            onClick={toggleSaved}
        >
            <img src={`/icons/spotify/like-icon-like${isSaved ? "d" : ""}.svg`} />
        </IconButton>
    );
};

export default SaveOnSpotifyButton;
