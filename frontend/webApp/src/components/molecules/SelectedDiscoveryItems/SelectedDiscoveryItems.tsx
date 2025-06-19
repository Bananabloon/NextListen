import { IconX } from "@tabler/icons-react";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./SelectedDiscoveryItems.module.css";
import cs from "classnames";
import ScrollingText from "../../atoms/ScrollingText/ScrollingText";
import { Dictionary, isEmpty, last } from "lodash";
import { DiscoveryType } from "../../../types/api.types";

type ImageEntry = { url: string } | undefined;

interface ItemSelectionContainerProps extends React.HTMLAttributes<HTMLDivElement> {
    type: DiscoveryType;
    data: any[];
    onRemoveItem: (index: number) => void;
}

const SelectedDiscoveryItems = ({
    onRemoveItem,
    type,
    data,
    children,
    className,
    ...props
}: ItemSelectionContainerProps): React.JSX.Element => {
    const getImageSource = {
        artists: (dataEntry: Dictionary<any>) => (last(dataEntry?.images) as ImageEntry)?.url,
        tracks: (dataEntry: Dictionary<any>) => (last(dataEntry?.album?.images) as ImageEntry)?.url,
    }[type];

    let items = data.map((dataEntry, i) => {
        return (
            <Group
                className={classes.selectionElement}
                style={{
                    borderRadius:
                        type === "genres" ? "var(--radius-sm)" : "var(--radius-xl) var(--radius-sm) var(--radius-sm) var(--radius-xl)",
                }}
                key={i}
            >
                {type !== "genres" && (
                    <img
                        className={classes.selectionElementPfp}
                        src={getImageSource?.(dataEntry)}
                    />
                )}
                <ScrollingText
                    style={{
                        flex: "1",
                        ...(type === "genres" && { paddingLeft: "var(--spacing-md)" }),
                    }}
                >
                    {dataEntry.name}
                </ScrollingText>
                <IconX
                    color="var(--text-color-disabled)"
                    size={20}
                    className={classes.removeIcon}
                    onClick={() => onRemoveItem(i)}
                />
            </Group>
        );
    });

    return type !== "top" ? (
        <Stack
            className={cs(classes.container, className)}
            {...props}
        >
            <p className={classes.label}>Selected {type}:</p>
            {isEmpty(items) ? <p className={classes.placeholder}>None selected yet</p> : <Stack className={classes.items}>{items}</Stack>}
        </Stack>
    ) : (
        <></>
    );
};

export default SelectedDiscoveryItems;
