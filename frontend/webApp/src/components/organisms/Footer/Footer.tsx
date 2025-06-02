import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import classes from "./Footer.module.css";
import PlayerSeekBar from "../../atoms/PlayerSeekBar/PlayerSeekBar";
import PlayerControls from "../../molecules/PlayerControls/PlayerControls";

const Footer = (): React.JSX.Element => {
    return (
        <div className={classes.container}>
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
