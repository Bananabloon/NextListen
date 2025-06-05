import { BarLoader, BounceLoader, ClimbingBoxLoader, GridLoader } from "react-spinners";
import Stack from "../../atoms/Stack/Stack";
import { useEffect, useState } from "react";
import classes from "./QueueLoadingOverlay.module.css";
import cs from "classnames";

const prompts = [
    "Collecting your listening data...",
    "Analyzing your musical taste...",
    "Identifying genres and patterns...",
    "Matching you with similar listeners...",
    "Digging through thousands of tracks...",
    "Selecting the perfect songs for you...",
    "Tuning the playlist to your vibe...",
    "Finalizing your personalized mix...",
    "Almost there — putting it all together...",
    "Your music recommendations are ready!",
];

interface QueueLoadingOverlayProps extends React.HTMLAttributes<HTMLDivElement> {}

const QueueLoadingOverlay = ({ className, ...props }: QueueLoadingOverlayProps): React.JSX.Element => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => setIndex((prev) => (prev + 1 === prompts.length ? 0 : prev + 1)), 3000);
        return () => clearInterval(interval);
    }, [index]);

    return (
        <Stack className={cs(classes.container, className)}>
            <GridLoader color="white" />
            <span className={classes.text}>{prompts[index]}</span>
        </Stack>
    );
};

export default QueueLoadingOverlay;
