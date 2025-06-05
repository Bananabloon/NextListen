import { useEffect, useRef, useState } from "react";
import { formatTime } from "../../../utils/datetime";
import Group from "../Group/Group";
import Stack from "../Stack/Stack";
import classes from "./PlayerSeekBar.module.css";
import cs from "classnames";
import { usePlayback } from "../../../contexts/PlaybackContext";
import { isNull } from "lodash";

interface PlayerSeekBarProps extends React.HTMLAttributes<HTMLDivElement> {}

const PlayerSeekBar = ({ className, ...props }: PlayerSeekBarProps): React.JSX.Element => {
    const { currentState, seek } = usePlayback();
    const [position, setPosition] = useState(0);

    useEffect(() => {
        setPosition(currentState?.position ?? 0);
    }, [currentState?.position]);

    const maxPosition = (currentState?.track_window?.current_track?.duration_ms ?? 0) || null;

    return (
        <Stack
            className={cs(className, classes.container)}
            {...props}
        >
            <Group className={classes.upper}>
                <span>{formatTime(position)}</span>
                <span>{isNull(maxPosition) ? "--:--" : formatTime(maxPosition)}</span>
            </Group>
            <input
                type="range"
                className={classes.range}
                value={position}
                min="0"
                max={maxPosition || 180000}
                disabled={isNull(maxPosition)}
                onChange={(e) => {
                    const newPosition = parseInt(e.currentTarget.value);
                    seek(newPosition);
                    setPosition(newPosition);
                }}
                style={
                    {
                        // "--progress-color": color,
                    } as React.CSSProperties
                }
            />
        </Stack>
    );
};

export default PlayerSeekBar;
