import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import SongCard from "../../molecules/SongCard/SongCard";
import React, { useEffect, useState } from "react";
import { remToPx } from "css-unit-converter-js";
import ScrollContainer from "react-indiana-drag-scroll";
import { useElementSize } from "@mantine/hooks";
import { useQueue } from "../../../contexts/QueueContext";
import SongCardPlaceholder from "../../molecules/SongCard/SongCardPlaceholder";
import SongCardLoading from "../../molecules/SongCard/SongCardLoading";

interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {}

const SongCardConveyor = ({ children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    const { queue, currentIndex, setCurrentIndex } = useQueue();
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
        const currentSnap = Math.floor((scrollCenter - cardWidth - selectedCardWidth - 2.5 * containerGap) / (containerGap + cardWidth));
        setCurrentIndex(currentSnap);
    };

    // manual snap implementation due to using grabbable scroll
    const snap = (toIndex: number, scrollBehavior = "smooth") => {
        const { cardWidth, selectedCardWidth, containerGap, containerWidth } = getDimensions();
        const snapPoint = (toIndex + 2) * (cardWidth + containerGap) + containerGap + selectedCardWidth / 2 - containerWidth / 2;
        ref.current.scrollTo({ left: snapPoint, behavior: scrollBehavior });
    };

    const onScroll = () => {
        if (ref.current && !suppressFocusUpdate) updateFocus();
    };

    const onEndScroll = () => {
        if (ref.current) snap(currentIndex);
    };

    useEffect(() => {
        if (ref.current) {
            setSuppressFocusUpdate(true);
            snap(currentIndex);

            const timeout = setTimeout(() => setSuppressFocusUpdate(false), 300);

            return () => clearTimeout(timeout);
        }
    }, [currentIndex]);

    useEffect(() => {
        if (ref.current) snap(currentIndex, "auto");
    }, [width]);

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
