import { useRef, useState } from "react";
import { formatTime } from "../../../utils/datetime";
import Group from "../Group/Group";
import Stack from "../Stack/Stack";
import classes from "./PlayerSeekBar.module.css";
import cs from "classnames";

interface PlayerSeekBarProps extends React.HTMLAttributes<HTMLDivElement> {}

const PlayerSeekBar = ({ className, ...props }: PlayerSeekBarProps): React.JSX.Element => {
    const [currentPosition, setCurrentPosition] = useState(123);
    let maxPosition = 384;
    let color = "";

    return (
        <Stack
            className={cs(className, classes.container)}
            {...props}
        >
            <Group className={classes.upper}>
                <span>{formatTime(currentPosition)}</span>
                <span>{formatTime(maxPosition)}</span>
            </Group>
            <input
                type="range"
                className={classes.range}
                min="0"
                max={maxPosition}
                value={currentPosition}
                onChange={(e) => setCurrentPosition(parseInt(e.currentTarget.value))}
                style={
                    {
                        "--progress-color": color,
                    } as React.CSSProperties
                }
            />
        </Stack>
    );
};

export default PlayerSeekBar;
