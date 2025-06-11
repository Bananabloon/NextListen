import { useEffect, useState } from "react";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import ModalController from "../../molecules/ModalController/ModalController";
import classes from "./DiscoveryModalController.module.css";
import ItemSelectionContainer from "../../molecules/ItemSelectionContainer/ItemSelectionContainer";
import FilteredSelect from "../../molecules/FilteredSelect/FilteredSelect";
import { useQueue } from "../../../contexts/QueueContext";
import SegmentedControl from "../../atoms/SegmentedControl/SegmentedControl";
import { DiscoveryType } from "../../../types/api.types";

const DiscoveryModalController = (): React.JSX.Element => {
    const [activeFilter, setActiveFilter] = useState<"top" | "top" | "artists" | "tracks" | "genres">("artists");
    const [items, setItems] = useState<any[]>([]);
    const { queue, createNewDiscoveryQueue } = useQueue();

    const spotifyToPathMap = {
        artists: "artist",
        tracks: "song",
        genres: "genre",
    };

    useEffect(() => {
        setItems([]);
    }, [activeFilter]);

    const addNewObject = (option) => {
        setItems((prev) => [...prev, option]);
    };

    const removeItem = (id) => {
        setItems((prev) => prev.filter((item, i) => i !== id));
    };

    const generateQueue = () => {
        let names = items.map((item) => item.name);
        let count = 20;
        let formattedItems;
        formattedItems = {
            count: count,
            [activeFilter === "artists" ? "artists" : activeFilter === "tracks" ? "titles" : activeFilter === "genres" ? "genre" : ""]:
                activeFilter !== "genres" ? names : names[0],
        };
        console.log(formattedItems);
        // }
        createNewDiscoveryQueue(spotifyToPathMap[activeFilter] as DiscoveryType, formattedItems);
    };

    return (
        <ModalController
            buttonText="Generate New Queue"
            width={816}
            height={500}
            className={classes.modal}
        >
            <h1 className={classes.title}>New Queue</h1>
            <Stack className={classes.content}>
                <Stack className={classes.itemsWithLabel}>
                    <p className={classes.label}>Based on:</p>
                    <SegmentedControl
                        options={[
                            { label: "My Top Songs", value: "top" },
                            { label: "Selected Artists", value: "artists" },
                            { label: "Selected Songs", value: "tracks" },
                            { label: "Selected Genres", value: "genres" },
                        ]}
                        buttonProps={{ className: classes.segmentedControlButton }}
                        value={activeFilter}
                        // ! to be removed
                        // @ts-ignore
                        onChange={setActiveFilter}
                    />
                </Stack>
                <Group className={classes.controlGroup}>
                    <FilteredSelect
                        filter={activeFilter}
                        changeSelectOption={addNewObject}
                    />
                    <ItemSelectionContainer
                        onRemoveItem={removeItem}
                        filter={activeFilter}
                        data={items}
                        className={classes.selectedItemsStack}
                    />
                </Group>
                <Button
                    size="md"
                    background="white"
                    className={classes.genButton}
                    onClick={generateQueue}
                >
                    Generate
                </Button>
            </Stack>
        </ModalController>
    );
};

export default DiscoveryModalController;
