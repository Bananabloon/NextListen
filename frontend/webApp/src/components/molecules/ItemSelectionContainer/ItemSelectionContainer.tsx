import { IconX } from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ItemSelectionContainer.module.css";
import cs from "classnames";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";
import { Dictionary, isEmpty, last } from "lodash";

type ImageEntry = { url: string } | undefined;

interface ItemSelectionContainerProps extends React.HTMLAttributes<HTMLDivElement> {
    filter: "top" | "artists" | "tracks" | "genres";
    data: any[];
    onRemoveItem: (index: number) => void;
}

const ItemSelectionContainer = ({
    onRemoveItem,
    filter,
    data,
    children,
    className,
    ...props
}: ItemSelectionContainerProps): React.JSX.Element => {
    const getImageSource = {
        artists: (dataEntry: Dictionary<any>) => (last(dataEntry?.images) as ImageEntry)?.url,
        tracks: (dataEntry: Dictionary<any>) => (last(dataEntry?.album?.images) as ImageEntry)?.url,
    }[filter];

    let items = data.map((dataEntry, i) => {
        return (
            <Group
                className={classes.selectionElement}
                key={i}
            >
                <img
                    className={classes.selectionElementPfp}
                    src={getImageSource?.(dataEntry)}
                />
                <ScrollingText style={{ flex: "1" }}>{dataEntry.name}</ScrollingText>
                <IconX
                    color="var(--text-color-disabled)"
                    size={20}
                    className={classes.removeIcon}
                    onClick={() => onRemoveItem(i)}
                />
            </Group>
        );
    });

    return (
        <Stack
            className={cs(classes.container, className)}
            {...props}
        >
            <p className={classes.label}>Selected {filter}:</p>
            {isEmpty(items) ? <p className={classes.placeholder}>None selected yet</p> : <Stack className={classes.items}>{items}</Stack>}
        </Stack>
    );
};

export default ItemSelectionContainer;
