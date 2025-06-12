import { useEffect, useRef, useState } from "react";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import ModalController, { ModalControllerHandle } from "../../molecules/ModalController/ModalController";
import classes from "./DiscoveryModalController.module.css";
import ItemSelectionContainer from "../../molecules/ItemSelectionContainer/ItemSelectionContainer";
import FilteredSelect from "../../molecules/FilteredSelect/FilteredSelect";
import SegmentedControl from "../../atoms/SegmentedControl/SegmentedControl";
import { useQueue } from "../../../contexts/QueueContext";
import { DiscoveryOptionsMap, DiscoveryType } from "../../../types/api.types";
import { IconPlaylistAdd } from "@tabler/icons-react";

const QUEUE_LENGTH = 20;

const DiscoveryModalController = ({ ...props }): React.JSX.Element => {
    const modalRef = useRef<ModalControllerHandle>(null);
    const [discoveryType, setDiscoveryType] = useState<DiscoveryType>("artists");
    const [items, setItems] = useState<any[]>([]);
    const { createNewDiscoveryQueue } = useQueue();

    useEffect(() => {
        setItems([]);
    }, [discoveryType]);

    const closeModal = () => modalRef.current?.close();

    const addNewObject = (newItem: any) => {
        setItems((prev) => [...prev, newItem]);
    };

    const removeItem = (idx: number) => {
        setItems((prev) => prev.filter((item, i) => i !== idx));
    };

    const generateQueue = <T extends DiscoveryType>() => {
        const names = items.map((item) => item.name);

        const typeSpecificOptions = {
            tracks: { titles: names },
            genres: { genres: names },
            artists: { artists: names },
        };
        const generationOptions = {
            count: QUEUE_LENGTH,
            ...(typeSpecificOptions[discoveryType] ?? {}),
        } as DiscoveryOptionsMap[T];

        createNewDiscoveryQueue(discoveryType, generationOptions);
        closeModal();
    };

    return (
        <ModalController
            buttonContent="Generate New Queue"
            width={820}
            height={500}
            onClose={() => setItems([])}
            ref={modalRef}
            buttonProps={{
                leftSection: <IconPlaylistAdd />,
                className: classes.openButton,
            }}
            {...props}
        >
            <Stack className={classes.container}>
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
                            value={discoveryType}
                            onChange={setDiscoveryType}
                        />
                    </Stack>
                    <Group className={classes.controlGroup}>
                        <FilteredSelect
                            type={discoveryType}
                            changeSelectOption={addNewObject}
                        />
                        <ItemSelectionContainer
                            onRemoveItem={removeItem}
                            type={discoveryType}
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
            </Stack>
        </ModalController>
    );
};

export default DiscoveryModalController;
