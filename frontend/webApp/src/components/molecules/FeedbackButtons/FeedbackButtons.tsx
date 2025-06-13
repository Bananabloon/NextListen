import { IconThumbDown, IconThumbDownFilled, IconThumbUp, IconThumbUpFilled } from "@tabler/icons-react";
import IconButton from "../../atoms/IconButton/IconButton";
import { useEffect, useState } from "react";
import { Feedback } from "../../../types/api.types";
import useRequests from "../../../hooks/useRequests";
import { useQueue } from "../../../contexts/QueueContext";

const FeedbackButtons = (): React.JSX.Element => {
    const { current } = useQueue();
    const [feedback, setFeedback] = useState<Feedback>(0);
    const { sendRequest } = useRequests();

    useEffect(() => {
        if (current?.uri) {
            sendRequest("GET", `songs/feedback/?spotify_uri=${current.uri}`).then((data) => setFeedback(data?.feedback_value ?? 0));
        }
    }, [current?.uri]);

    const updateFeedback = (value: Feedback) => {
        setFeedback(value);
        sendRequest("POST", "songs/feedback/update", {
            body: JSON.stringify({ spotify_uri: current.uri, feedback_value: value }),
        });
    };

    return (
        <>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => updateFeedback(feedback === -1 ? 0 : -1)}
            >
                {feedback === -1 ? (
                    <IconThumbDownFilled style={{ transform: "scaleX(-1) translateY(2px)" }} />
                ) : (
                    <IconThumbDown style={{ transform: "scaleX(-1) translateY(2px)" }} />
                )}
            </IconButton>
            <IconButton
                size="md"
                variant="transparent"
                onClick={() => updateFeedback(feedback === 1 ? 0 : 1)}
            >
                {feedback === 1 ? (
                    <IconThumbUpFilled
                        style={{
                            transform: "translateY(-2px)",
                        }}
                    />
                ) : (
                    <IconThumbUp
                        style={{
                            transform: "translateY(-2px)",
                        }}
                    />
                )}
            </IconButton>
        </>
    );
};

export default FeedbackButtons;
