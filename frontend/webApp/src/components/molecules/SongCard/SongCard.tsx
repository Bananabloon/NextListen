import classes from "./SongCard.module.css";
import cs from "classnames";
import { IconThumbDown } from "@tabler/icons-react";
import { IconThumbUp } from "@tabler/icons-react";
import IconButton from "../../atoms/IconButton/IconButton";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import { IconThumbDownFilled } from "@tabler/icons-react";
import { IconThumbUpFilled } from "@tabler/icons-react";
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
            <Stack style={{ gap: "0" }}>
                {song.curveball && <p className={classes.curveballText}>Curveball</p>}
                <p className={classes.titleText}>{song.name}</p>
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
