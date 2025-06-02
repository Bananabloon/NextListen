import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import Group from "../../atoms/Group/Group";
import SongCard from "../../molecules/SongCard/SongCard";
import type { Song } from "../../molecules/SongCard/SongCard";
let songs: Song[] = [
    {
        name: "NASA",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:4uTvPEr01pjTbZgl7jcKBD",
        images: [
            {
                url: "https://i.scdn.co/image/ab67616d0000b27356ac7b86e090f307e218e9c8",
                height: 640,
                width: 640,
            },
        ],
    },
];
interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {}

const SongCardConveyor = ({ children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    return (
        <div
            className={cs(classes.conveyor, className)}
            {...props}
        >
            <div className={classes.conveyorShadow}></div>
            <Group
                className={classes.cards}
                style={{ gap: "40px", justifyContent: "center", marginBottom: "150px" }}
            >
                <SongCard song={songs[0]} />
                <SongCard song={songs[0]} />
                <SongCard
                    song={songs[0]}
                    front
                />
                <SongCard song={songs[0]} />
                <SongCard song={songs[0]} />
            </Group>
        </div>
    );
};

export default SongCardConveyor;
