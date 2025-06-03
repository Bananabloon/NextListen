import { IconThumbDown, IconThumbDownFilled, IconThumbUp, IconThumbUpFilled } from "@tabler/icons-react";
import cs from "classnames";
import Group from "../../atoms/Group/Group";
import IconButton from "../../atoms/IconButton/IconButton";
import Stack from "../../atoms/Stack/Stack";
import classes from "./SongCard.module.css";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";

interface SongCardProps extends React.HTMLAttributes<HTMLDivElement> {
    song: Song;
    front?: boolean;
}
type ImageObject = {
    url: string;
    height: number;
    width: number;
};
export interface Song {
    curveball?: boolean;
    name: string;
    artists: string;
    duration_ms: number;
    uri: string;
    images: ImageObject[];
}

const SongCard = ({ song, children, className, ...props }: SongCardProps): React.JSX.Element => {
    let feedback = 0;
    let image = song.images[0];
    let imageUrl = image.url;

    return (
        <Stack
            className={
                props.front
                    ? song.curveball
                        ? cs(classes.card, classes.cardCurveball)
                        : classes.card
                    : song.curveball
                      ? cs(classes.card, classes.cardBack, classes.cardCurveball)
                      : cs(classes.card, classes.cardBack)
            }
            {...props}
        >
            <img
                className={classes.cardImage}
                src={imageUrl}
            />
            <Stack className={classes.metadata}>
                {song.curveball && <p className={classes.curveballText}>Curveball</p>}
                <ScrollingText speed={60}>
                    <p className={classes.titleText}>{song.name}</p>
                </ScrollingText>
                <p className={classes.artistsText}>{song.artists}</p>
            </Stack>
            <Group className={classes.controlGroup}>
                {props.front ? (
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
                            {feedback === -1 ? (
                                <IconThumbDownFilled style={{ transform: "scaleX(-1)" }} />
                            ) : (
                                <IconThumbDown style={{ transform: "scaleX(-1)" }} />
                            )}
                        </IconButton>
                        <IconButton
                            variant="transparent"
                            style={{ paddingLeft: "0" }}
                        >
                            {feedback === 1 ? <IconThumbUpFilled /> : <IconThumbUp />}
                        </IconButton>
                    </>
                )}
                <img
                    className={classes.spotifyLogo}
                    src="/icons/spotify/logo_white.svg"
                />
            </Group>
        </Stack>
    );
};

export default SongCard;
