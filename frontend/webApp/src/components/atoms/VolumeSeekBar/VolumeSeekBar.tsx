import classes from "./VolumeSeekBar.module.css";
import cs from "classnames";
import { IconVolume, IconVolumeOff } from "@tabler/icons-react";
import IconButton from "../IconButton/IconButton";
import { useEffect, useState } from "react";
import Group from "../Group/Group";
import { usePlayback } from "../../../contexts/PlaybackContext";
import { isNull } from "lodash";

interface VolumeSeekBarProps extends React.HTMLAttributes<HTMLDivElement> {}

const VolumeSeekBar = ({ className, ...props }: VolumeSeekBarProps): React.JSX.Element => {
    const { currentState, setVolume } = usePlayback();
    const [volume, setVolumeState] = useState(0);
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
            <Group>
                <IconButton
                    size="md"
                    variant="transparent"
                    onMouseEnter={(e) => setShowBar(true)}
                    onClick={toggleMute}
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
                    onMouseLeave={(e) => setShowBar(false)}
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={volume}
                    className={muted ? cs(classes.seekBar, classes.seekBarDisabled) : cs(classes.seekBar)}
                    style={{
                        opacity: showBar ? 1 : 0,
                        transition: "opacity 0.3s ease-in-out",
                    }}
                    disabled={muted}
                ></input>
            </Group>
        </div>
    );
};

export default VolumeSeekBar;
