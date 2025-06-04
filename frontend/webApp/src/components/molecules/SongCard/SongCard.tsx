import { IconThumbDown, IconThumbDownFilled, IconThumbUp, IconThumbUpFilled } from "@tabler/icons-react";
import cs from "classnames";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import Stack from "../../atoms/Stack/Stack";
import classes from "./SongCard.module.css";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";
import { GeneratedSong } from "../../../types/api.types";
import { isEmpty } from "lodash";

interface SongCardProps extends React.HTMLAttributes<HTMLDivElement> {
    song: GeneratedSong;
    isSelected?: boolean;
}

const SongCard = ({ isSelected = false, song, children, className, ...props }: SongCardProps): React.JSX.Element => {
    return (
        <Stack
            className={cs(classes.card)}
            {...props}
            data-selected={isSelected}
            data-curveball={song.curveball}
        >
            {!isEmpty(song) && (
                <>
                    <img
                        className={classes.cardImage}
                        src={song.track_details.album_cover}
                        draggable="false"
                        loading="lazy"
                    />
                    <Stack className={classes.metadata}>
                        {song.curveball && <p className={classes.curveballText}>Curveball</p>}
                        <ScrollingText speed={60}>
                            <p className={classes.titleText}>{song.track_details.name}</p>
                        </ScrollingText>
                        <p className={classes.artistsText}>{song.track_details.artists.join(", ")}</p>
                    </Stack>
                    <Group className={classes.controlGroup}>
                        {isSelected ? (
                            <a
                                href={song.uri}
                                style={{ alignSelf: "center" }}
                            >
                                OPEN ON SPOTIFY
                            </a>
                        ) : (
                            <>
                                <IconButton
                                    variant="transparent"
                                    style={{ alignItems: "flex-end", alignSelf: "center", marginLeft: "-10px" }}
                                >
                                    {song.feedback_value === -1 ? (
                                        <IconThumbDownFilled style={{ transform: "scaleX(-1)" }} />
                                    ) : (
                                        <IconThumbDown style={{ transform: "scaleX(-1)" }} />
                                    )}
                                </IconButton>
                                <IconButton
                                    variant="transparent"
                                    style={{ paddingLeft: "0" }}
                                >
                                    {song.feedback_value === 1 ? <IconThumbUpFilled /> : <IconThumbUp />}
                                </IconButton>
                            </>
                        )}
                        <img
                            className={classes.spotifyLogo}
                            src="/icons/spotify/logo_white.svg"
                        />
                    </Group>
                </>
            )}
        </Stack>
    );
};

export default SongCard;
