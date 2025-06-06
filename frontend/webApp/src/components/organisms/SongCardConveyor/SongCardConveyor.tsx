import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import SongCard from "../../molecules/SongCard/SongCard";
import React, { useEffect, useState } from "react";
import { GeneratedSong } from "../../../types/api.types";
import { remToPx } from "css-unit-converter-js";
import ScrollContainer from "react-indiana-drag-scroll";
import { useElementSize } from "@mantine/hooks";
import { isEmpty } from "lodash";
import { useQueue } from "../../../contexts/QueueContext";
import { usePlayback } from "../../../contexts/PlaybackContext";
import SongCardPlaceholder from "../../molecules/SongCard/SongCardPlaceholder";
import Stack from "../../atoms/Stack/Stack";
import { GridLoader } from "react-spinners";
import SongCardLoading from "../../molecules/SongCard/SongCardLoading";

interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {}

const SongCardConveyor = ({ children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    const { queue, currentIndex, setCurrentIndex, generateDiscoveryFromTop } = useQueue();
    const { width, ref } = useElementSize();
    const [suppressFocusUpdate, setSuppressFocusUpdate] = useState(false);

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
        setCurrentIndex(currentSnap);
    };

    // manual snap implementation due to using grabbable scroll
    const snap = (toIndex: number) => {
        const { cardWidth, selectedCardWidth, containerGap, containerWidth } = getDimensions();
        const snapPoint =
            (toIndex + 2) * (cardWidth + containerGap) + containerGap + selectedCardWidth / 2 - containerWidth / 2;
        ref.current.scrollTo({ left: snapPoint, behavior: "smooth" });
    };

    const onScroll = () => {
        if (ref.current && !suppressFocusUpdate) updateFocus();
    };

    const onEndScroll = () => {
        if (ref.current) snap(currentIndex);
    };

    useEffect(() => {
        if (isEmpty(queue)) generateDiscoveryFromTop();
    }, []);

    useEffect(() => {
        if (ref.current) {
            setSuppressFocusUpdate(true);
            snap(currentIndex);

            // Allow time for smooth scroll to complete before re-enabling focus updates
            const timeout = setTimeout(() => setSuppressFocusUpdate(false), 300);

            return () => clearTimeout(timeout);
        }
    }, [width, currentIndex]);

    const songCards = queue.map((song, i) => (
        <SongCard
            key={i}
            song={song}
            isSelected={i === currentIndex}
        />
    ));

    return (
        <div
            className={cs(classes.conveyor, className)}
            {...props}
            draggable="false"
        >
            <ScrollContainer
                horizontal
                vertical={false}
                onScroll={onScroll}
                onEndScroll={onEndScroll}
                className={cs(classes.cards, "scroll-container")}
                innerRef={ref}
            >
                <SongCardPlaceholder transparent />
                <SongCardPlaceholder transparent />
                {songCards}
                <SongCardLoading />
                <SongCardPlaceholder transparent />
            </ScrollContainer>
            <div className={classes.conveyorShadow} />
        </div>
    );
};

export default SongCardConveyor;
