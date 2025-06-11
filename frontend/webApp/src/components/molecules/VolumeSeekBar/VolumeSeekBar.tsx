import classes from "./VolumeSeekBar.module.css";
import cs from "classnames";
import { IconVolume, IconVolumeOff } from "@tabler/icons-react";
import IconButton from "../../atoms/IconButton/IconButton";
import { useEffect, useState } from "react";
import Group from "../../atoms/Group/Group";
import { usePlayback } from "../../../contexts/PlaybackContext";
import { isNull } from "lodash";
import Stack from "../../atoms/Stack/Stack";

interface VolumeSeekBarProps extends React.HTMLAttributes<HTMLDivElement> {}

const VolumeSeekBar = ({ className, ...props }: VolumeSeekBarProps): React.JSX.Element => {
    const { currentState, setVolume } = usePlayback();
    const [volume, setVolumeState] = useState(0.2);
    const [muted, setMuted] = useState(false);
    const [showBar, setShowBar] = useState(false);

    useEffect(() => {
        if (!muted && !isNull(currentState)) setVolume(volume);
    }, [volume, muted]);

    const toggleMute = () =>
        setMuted((prev) => {
            if (!prev) setVolume(0);
            return !prev;
        });

    return (
        <div
            className={cs(classes.container, className)}
            {...props}
        >
            <Group className={classes.widthAligner}>
                <div className={classes.wrapper}>
                    <IconButton
                        size="md"
                        variant="transparent"
                        onMouseEnter={() => setShowBar(true)}
                        onClick={toggleMute}
                        className={classes.speakerIcon}
                    >
                        {muted ? (
                            <IconVolumeOff
                                size={32}
                                style={{ alignSelf: "center" }}
                            />
                        ) : (
                            <IconVolume
                                size={32}
                                style={{ alignSelf: "center" }}
                            />
                        )}
                    </IconButton>
                    <input
                        onChange={(e) => {
                            setVolumeState(parseFloat(e.target.value));
                        }}
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        className={muted ? cs(classes.seekBar, classes.seekBarDisabled) : cs(classes.seekBar)}
                        style={{
                            opacity: showBar ? 1 : 0,
                            transition: "opacity 0.3s ease-in-out",
                            cursor: showBar ? "pointer" : "default",
                        }}
                        disabled={muted || !showBar}
                    ></input>
                </div>
            </Group>
        </div>
    );
};

export default VolumeSeekBar;
