import {
    IconPlayerPauseFilled,
    IconPlayerPlayFilled,
    IconPlayerTrackNextFilled,
    IconPlayerTrackPrevFilled,
    IconRocket,
    IconThumbDown,
    IconThumbDownFilled,
    IconThumbUp,
    IconThumbUpFilled,
} from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import classes from "./Footer.module.css";
import PlayerSeekBar from "../../atoms/PlayerSeekBar/PlayerSeekBar";

const Footer = (): React.JSX.Element => {
    const [feedback, previousExists, nextExists, playing, saved, curveballs] = [-1, false, true, true, false, false];

    return (
        <div className={classes.container}>
            <div className={classes.seekBarPositioner}>
                <PlayerSeekBar className={classes.playerSeekBar} />
            </div>
            <Group className={classes.footer}>
                <Group className={classes.leftSection}></Group>
                <Group className={classes.centralSection}>
                    <IconButton
                        size="md"
                        variant="transparent"
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
                    <IconButton
                        size="md"
                        variant="transparent"
                        disabled={!previousExists}
                    >
                        <IconPlayerTrackPrevFilled />
                    </IconButton>
                    <IconButton
                        size="sm"
                        variant="filled"
                        style={{ borderRadius: "50%" }}
                    >
                        {playing ? <IconPlayerPauseFilled /> : <IconPlayerPlayFilled />}
                    </IconButton>
                    <IconButton
                        size="md"
                        variant="transparent"
                        disabled={!nextExists}
                    >
                        <IconPlayerTrackNextFilled />
                    </IconButton>
                    <IconButton
                        size="md"
                        variant="transparent"
                    >
                        <img src={`/icons/spotify/like-icon-like${saved ? "d" : ""}.svg`} />
                    </IconButton>
                    <IconButton
                        size="md"
                        variant="transparent"
                    >
                        {curveballs ? (
                            <IconRocket />
                        ) : (
                            <img
                                src={`/icons/tabler/rocket-x.svg`}
                                style={{ filter: "invert(100%)" }}
                            />
                        )}
                    </IconButton>
                </Group>
                <Group className={classes.rightSection}></Group>
            </Group>
        </div>
    );
};

export default Footer;
