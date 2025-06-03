import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import Group from "../../atoms/Group/Group";
import SongCard from "../../molecules/SongCard/SongCard";
import type { Song } from "../../molecules/SongCard/SongCard";
import { useState } from "react";
// import { motion } from "motion/react";
// import { useAnimate } from "motion/react";
let emptySong = {
    name: "None",
    artists: "None",
    duration_ms: 0,
    uri: "",
    images: [
        {
            url: "https://encycolorpedia.pl/000000.png",
            height: 640,
            width: 640,
        },
    ],
};

let songs: Song[] = [
    {
        name: "NASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
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
    {
        name: "break up with your girlfriend, i'm bored",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:4kV4N9D1iKVxx1KLvtTpjS?si=c006601dda004822",
        images: [
            {
                url: "https://i.scdn.co/image/ab67616d0000b27356ac7b86e090f307e218e9c8",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        curveball: true,
        name: "thank u, next",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:3e9HZxeyfWwjeyPAMmWSSQ?si=9e111d14c16b4503",
        images: [
            {
                url: "https://i.scdn.co/image/ab67616d0000b27356ac7b86e090f307e218e9c8",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        name: "imagine",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:39LmTF9RgyakzSYX8txrow?si=76a085f58b1442f4",
        images: [
            {
                url: "https://i.scdn.co/image/ab67616d0000b27356ac7b86e090f307e218e9c8",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        name: "7 rings",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:6ocbgoVGwYJhOv1GgI9NsF?si=9783d66855814298",
        images: [
            {
                url: "https://i.scdn.co/image/ab67616d0000b27356ac7b86e090f307e218e9c8",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        name: "breathin",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:4OafepJy2teCjYJbvFE60J?si=997caa5ef7c345a0",
        images: [
            {
                url: "https://cdn-images.dzcdn.net/images/cover/8a5d4fa5c1b97100bf128909d766f06f/0x1900-000000-80-0-0.jpg",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        name: "R.E.M",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:1xWH8zYtDeS9mW1JJG23VZ?si=6faa8f8c0eab4208",
        images: [
            {
                url: "https://cdn-images.dzcdn.net/images/cover/8a5d4fa5c1b97100bf128909d766f06f/0x1900-000000-80-0-0.jpg",
                height: 640,
                width: 640,
            },
        ],
    },
    {
        name: "God is a woman",
        artists: "Ariana Grande",
        duration_ms: 3000,
        uri: "spotify:track:5OCJzvD7sykQEKHH7qAC3C?si=d9e4b5f23b27421c",
        images: [
            {
                url: "https://cdn-images.dzcdn.net/images/cover/8a5d4fa5c1b97100bf128909d766f06f/0x1900-000000-80-0-0.jpg",
                height: 640,
                width: 640,
            },
        ],
    },
];
interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {}
const getSongs = async () => {
    //
};
const SongCardConveyor = ({ children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    const [currentCardUri, setCurrentCardUri] = useState(songs[2].uri);
    // const [scope, animate] = useAnimate();
    const songCards = songs.map((song) => (
        <SongCard
            key={song.uri}
            className={classes.card}
            song={song}
            front={song.uri === currentCardUri}
            style={{
                marginLeft: song.uri === songs[0].uri ? "auto" : "0",
                marginRight: song.uri === songs[songs.length - 1].uri ? "auto" : "0",
            }}
        />
    ));
    return (
        <div
            className={cs(classes.conveyor, className)}
            {...props}
        >
            <div className={classes.conveyorShadow}></div>
            <Group
                className={classes.cards}
                style={{
                    gap: "40px",
                    marginBottom: "150px",
                }}
            >
                {songCards}
            </Group>
        </div>
    );
};

export default SongCardConveyor;
