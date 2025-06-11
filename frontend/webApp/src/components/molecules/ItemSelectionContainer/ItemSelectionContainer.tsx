import { IconX } from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./ItemSelectionContainer.module.css";
import cs from "classnames";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";

interface ItemSelectionContainerProps extends React.HTMLAttributes<HTMLDivElement> {
    onRemoveItem: Function;
    filter: "artists" | "tracks" | "genres";
    data: any[];
}

const ItemSelectionContainer = ({
    onRemoveItem,
    filter,
    data,
    children,
    className,
    ...props
}: ItemSelectionContainerProps): React.JSX.Element => {
    let items = data.map((dataObject, i) => {
        return (
            <Group
                className={classes.selectionElement}
                key={i}
            >
                <img
                    className={classes.selectionElementPfp}
                    src={
                        filter === "artists" && dataObject.images?.length > 0
                            ? dataObject.images[dataObject.images.length - 1].url
                            : filter === "tracks" && dataObject.album?.images?.length > 0
                              ? dataObject.album.images[dataObject.album.images.length - 1].url
                              : ""
                    }
                />
                <ScrollingText style={{ flex: "1" }}>{dataObject.name}</ScrollingText>
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
            className={cs(classes.selectionViewContainer, className)}
            {...props}
        >
            <h3>Selected {filter}:</h3>
            {items}
        </Stack>
    );
};

export default ItemSelectionContainer;
