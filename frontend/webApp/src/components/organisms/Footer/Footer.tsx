import Group from "../../atoms/Group/Group";
import classes from "./Footer.module.css";
import PlayerControls from "../../molecules/PlayerControls/PlayerControls";
import { useQueue } from "../../../contexts/QueueContext";
import PlayerSeekBar from "../../molecules/PlayerSeekBar/PlayerSeekBar";
import DiscoveryModalController from "../DiscoveryModalController/DiscoveryModalController";
import { isEmpty } from "lodash";

const Footer = (): React.JSX.Element => {
    const { queue, loading } = useQueue();
    return (
        <div
            className={classes.container}
            style={{ display: isEmpty(queue) || loading ? "none" : "flex" }}
        >
            <div className={classes.seekBarPositioner}>
                <PlayerSeekBar className={classes.playerSeekBar} />
            </div>
            <Group className={classes.footer}>
                <Group className={classes.leftSection}>
                    <DiscoveryModalController />
                </Group>
                <PlayerControls className={classes.centralSection} />
                <Group className={classes.rightSection}></Group>
            </Group>
        </div>
    );
};

export default Footer;
