import Group from "../../atoms/Group/Group";
import classes from "./Footer.module.css";
import PlayerControls from "../../molecules/PlayerControls/PlayerControls";
import { useQueue } from "../../../contexts/QueueContext";
import PlayerSeekBar from "../../molecules/PlayerSeekBar/PlayerSeekBar";

const Footer = (): React.JSX.Element => {
    const { loading } = useQueue();
    return (
        <div
            className={classes.container}
            style={{ display: loading ? "none" : "flex" }}
        >
            <div className={classes.seekBarPositioner}>
                <PlayerSeekBar className={classes.playerSeekBar} />
            </div>
            <Group className={classes.footer}>
                <Group className={classes.leftSection}></Group>
                <PlayerControls className={classes.centralSection} />
                <Group className={classes.rightSection}></Group>
            </Group>
        </div>
    );
};

export default Footer;
