import cs from "classnames";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./SongCard.module.css";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";
import { GeneratedSong } from "../../../types/api.types";

interface SongCardProps extends React.HTMLAttributes<HTMLDivElement> {
    song: GeneratedSong;
    isSelected?: boolean;
    isPlaceholder?: boolean;
}

const SongCard = ({ isPlaceholder, isSelected = false, song, children, className, ...props }: SongCardProps): React.JSX.Element => {
    return (
        <Stack
            className={cs(classes.card)}
            {...props}
            data-selected={isSelected}
            data-curveball={song.curveball}
            style={{ visibility: isPlaceholder ? "hidden" : "visible" }}
        >
            <img
                className={classes.cardImage}
                src={song?.track_details?.album_cover}
                draggable="false"
                loading="lazy"
            />
            <Stack className={classes.metadata}>
                {song?.curveball && <p className={classes.curveballText}>Curveball</p>}
                <ScrollingText speed={60}>
                    <p className={classes.titleText}>{song?.track_details?.name}</p>
                    <p className={classes.artistsText}>{song?.track_details?.artists?.join(", ")}</p>
                </ScrollingText>
            </Stack>
            <Group className={classes.controlGroup}>
                <a
                    href={song?.uri}
                    className={classes.link}
                    target="_blank"
                >
                    OPEN ON SPOTIFY
                </a>
                <img
                    className={classes.spotifyLogo}
                    src="/icons/spotify/logo_white.svg"
                />
            </Group>
        </Stack>
    );
};

export default SongCard;
