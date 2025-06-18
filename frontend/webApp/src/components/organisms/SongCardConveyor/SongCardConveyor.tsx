import classes from "./SongCardConveyor.module.css";
import cs from "classnames";
import SongCard from "../../molecules/SongCard/SongCard";
import React, { useEffect, useImperativeHandle, useRef } from "react";
import { useQueue } from "../../../contexts/QueueContext";
import { Virtuoso, VirtuosoHandle } from "react-virtuoso";
import { isNull } from "lodash";
import { GeneratedSong } from "../../../types/api.types";

const PLACEHOLDERS_PER_SIDE = 2;

interface SongCardConveyorProps extends React.HTMLAttributes<HTMLDivElement> {
    shouldSnap: boolean;
    setShouldSnap: Function;
}

const SongCardConveyor = ({ shouldSnap, setShouldSnap, children, className, ...props }: SongCardConveyorProps): React.JSX.Element => {
    const { queue, currentIndex, setCurrentIndex } = useQueue();
    const virtuoso = useRef<VirtuosoHandle>(null);

    const snap = (smooth = true) => {
        virtuoso.current!.scrollToIndex({
            index: currentIndex + 2,
            align: "center",
            behavior: smooth ? "smooth" : "auto",
        });
    };

    const handleLoad = () => {
        if (!shouldSnap) return;

        setTimeout(() => {
            snap(true);
            setShouldSnap(false);
        }, 300);
    };

    const handleClick = (e: React.MouseEvent<HTMLDivElement, MouseEvent>, index: number) => {
        e.stopPropagation();
        setCurrentIndex(index);
    };

    useEffect(() => {
        if (!isNull(currentIndex)) snap();
    }, [currentIndex]);

    const data = [...Array(PLACEHOLDERS_PER_SIDE).fill(null), ...queue, ...Array(PLACEHOLDERS_PER_SIDE).fill(null)];

    return (
        <div
            className={cs(classes.conveyor, className)}
            {...props}
            draggable="false"
        >
            <Virtuoso
                className={classes.virtuoso}
                horizontalDirection
                initialTopMostItemIndex={currentIndex}
                ref={virtuoso}
                rangeChanged={handleLoad}
                data={data}
                itemContent={(i, song) => (
                    <SongCard
                        key={i}
                        song={song ?? ({} as GeneratedSong)}
                        onClick={(e) => handleClick(e, i - PLACEHOLDERS_PER_SIDE)}
                        isSelected={i - PLACEHOLDERS_PER_SIDE === currentIndex}
                        isPlaceholder={isNull(song)}
                    />
                )}
            />
            <div className={classes.conveyorShadow} />
        </div>
    );
};

export default SongCardConveyor;
