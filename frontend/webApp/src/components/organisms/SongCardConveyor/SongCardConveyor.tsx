import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import SongCard from "../../molecules/SongCard/SongCard";
import React, { useEffect, useState } from "react";
import useRequests from "../../../hooks/useRequests";
import { GeneratedSong } from "../../../types/api.types";
import { remToPx } from "css-unit-converter-js";
import ScrollContainer from "react-indiana-drag-scroll";
import { useElementSize } from "@mantine/hooks";
import { isEmpty } from "lodash";
import { SyncLoader } from "react-spinners";
import { usePlayback } from "../../../contexts/PlaybackContext";

interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {}

const SongCardConveyor = ({ children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    const [songs, setSongs] = useState<GeneratedSong[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [selectedIndex, setSelectedIndex] = useState<number>(0);
    const { width, ref } = useElementSize();
    const { sendRequest } = useRequests();
    const { playTrack, currentState } = usePlayback();

    const getDimensions = () => {
        const container = ref.current!;
        const styles = getComputedStyle(container);

        return {
            cardWidth: container.querySelector('*[data-selected="false"]')?.getBoundingClientRect().width ?? 0,
            selectedCardWidth: container.querySelector('*[data-selected="true"]')?.getBoundingClientRect().width ?? 0,
            containerGap: remToPx(parseFloat(styles.getPropertyValue("--conveyor-gap"))),
            scrollCenter: container.scrollLeft + container.clientWidth / 2,
            containerWidth: container.clientWidth,
        };
    };

    // sets currently focused
    const updateFocus = () => {
        const { cardWidth, selectedCardWidth, containerGap, scrollCenter } = getDimensions();
        const currentSnap = Math.floor(
            (scrollCenter - cardWidth - selectedCardWidth - 2.5 * containerGap) / (containerGap + cardWidth)
        );
        setSelectedIndex(currentSnap);
    };

    // manual snap implementation due to using grabbable scroll
    const snap = (toIndex: number) => {
        const { cardWidth, selectedCardWidth, containerGap, containerWidth } = getDimensions();
        const snapPoint =
            (toIndex + 2) * (cardWidth + containerGap) + containerGap + selectedCardWidth / 2 - containerWidth / 2;
        ref.current.scrollTo({ left: snapPoint, behavior: "smooth" });
    };

    const onScroll = () => {
        if (ref.current) updateFocus();
    };

    const onEndScroll = () => {
        if (ref.current) snap(selectedIndex);
    };

    useEffect(() => {
        if (ref.current) snap(selectedIndex);
    }, [width]);

    useEffect(() => {
        if (isEmpty(songs)) {
            setLoading(true);
            sendRequest("POST", "/songs/generate-from-top/", { body: JSON.stringify({ count: 10 }) }).then((data) => {
                setSongs(data?.songs ?? []);
                setLoading(false);
            });
        }
    }, []);

    useEffect(() => {
        if (!isEmpty(songs) && currentState?.track_window.current_track.uri !== songs[selectedIndex].uri) {
            playTrack(songs[selectedIndex].uri);
        }
    }, [selectedIndex]);

    const emptySongCard = (
        <SongCard
            song={{} as GeneratedSong}
            style={{ visibility: "hidden" }}
        />
    );

    const songCards = songs.map((song, i) => (
        <SongCard
            key={i}
            song={song}
            onClick={() => {
                playTrack(song.uri);
                snap(i);
            }}
            isSelected={i === selectedIndex}
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
            draggable="false"
        >
            {loading && (
                <SyncLoader
                    style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                        zIndex: 100,
                    }}
                    color="white"
                />
            )}
            <ScrollContainer
                horizontal
                vertical={false}
                onScroll={onScroll}
                onEndScroll={onEndScroll}
                className={cs(classes.cards, "scroll-container")}
                innerRef={ref}
            >
                {emptySongCard}
                {emptySongCard}
                {songCards}
                {emptySongCard}
                {emptySongCard}
            </ScrollContainer>
            <div className={classes.conveyorShadow} />
        </div>
    );
};

export default SongCardConveyor;
