import { useEffect, useState } from "react";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import ModalController from "../../molecules/ModalController/ModalController";
import classes from "./DiscoveryModalController.module.css";
import ItemSelectionContainer from "../../molecules/ItemSelectionContainer/ItemSelectionContainer";
import FilteredSelect from "../../molecules/FilteredSelect/FilteredSelect";
interface DiscoveryModalControllerProps extends React.HTMLAttributes<HTMLDivElement> {}
const DiscoveryModalController = ({
    children,
    className,
    ...props
}: DiscoveryModalControllerProps): React.JSX.Element => {
    const [activeFilter, setActiveFilter] = useState<"artists" | "tracks" | "genres">("artists");
    const [items, setItems] = useState<any[]>([]);

    useEffect(() => {
        setItems([]);
    }, [activeFilter]);

    const addNewObject = (option) => {
        setItems((prev) => [...prev, option]);
    };

    return (
        <ModalController
            buttonText="Generate New Queue"
            width={816}
            height={500}
        >
            <h1 className={classes.modalTitleText}>New Queue</h1>
            <h3 className={classes.supportiveText}>Based on:</h3>
            <Group
                className={classes.selectorsGroup}
                style={{ gap: "0", justifyContent: "center" }}
            >
                <Button
                    size="sm"
                    // onClick={() => setActiveFilter()}
                >
                    My Top Songs
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter("artists")}
                >
                    Selected Artists
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter("tracks")}
                >
                    Selected Songs
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter("genres")}
                >
                    Selected Genres
                </Button>
            </Group>
            <Stack>
                <Group>
                    <FilteredSelect
                        filter={activeFilter}
                        changeSelectOption={addNewObject}
                    />
                    <ItemSelectionContainer
                        filter={activeFilter}
                        data={items}
                    />
                </Group>
                <Button
                    size="md"
                    background="white"
                    className={classes.genButton}
                >
                    Generate
                </Button>
            </Stack>
        </ModalController>
    );
};

export default DiscoveryModalController;
