import { useQueue } from "../../../contexts/QueueContext";
import useRequests from "../../../hooks/useRequests";
import { ButtonProps } from "../../atoms/Button/Button";
import IconButton from "../../atoms/IconButton/IconButton";

interface SaveOnSpotifyButtonProps extends ButtonProps {}

const SaveOnSpotifyButton = ({ ...props }: SaveOnSpotifyButtonProps): React.JSX.Element => {
    const { current } = useQueue();
    const { sendRequest } = useRequests();

    const toggleSaved = () => {};

    return (
        <IconButton
            size="md"
            {...props}
            variant="transparent"
            onClick={toggleSaved}
        >
            <img src={`/icons/spotify/like-icon-like${false ? "d" : ""}.svg`} />
        </IconButton>
    );
};

export default SaveOnSpotifyButton;
