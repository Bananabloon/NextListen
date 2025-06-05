import { useEffect, useState } from "react";
import Button from "../../atoms/Button/Button";
import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import ModalController from "../../molecules/ModalController/ModalController";
import classes from "./DiscoveryModalController.module.css";
import cs from "classnames";
import { IconX } from "@tabler/icons-react";
import AsyncSelect from "react-select/async";
import useRequests from "../../../hooks/useRequests";
interface DiscoveryModalControllerProps extends React.HTMLAttributes<HTMLDivElement> {}

const DiscoveryModalController = ({
    children,
    className,
    ...props
}: DiscoveryModalControllerProps): React.JSX.Element => {
    const [activeFilter, setActiveFilter] = useState<number>(0);
    const [artists, setArtists] = useState<string[]>([]);
    const [songs, setSongs] = useState<string[]>([]);
    const [prompt, setPrompt] = useState<string>("");
    const filters: string[] = ["Top Songs", "Artists", "Songs", "Genres"];
    const filtersQueryName: string[] = ["", "artist", "song", "genre"];
    let filterAmount = 4;

    useEffect(() => {
        console.log(artists);
    }, [artists]);

    useEffect(() => {
        console.log(songs);
    }, [songs]);

    useEffect(() => {
        console.log(prompt);
    }, [prompt]);

    const options = [
        {
            value: "arianagrande",
            label: "Ariana Grande",
        },
    ];

    const requests = useRequests();
    const loadOptions = async (inputValue: string, callback) => {
        const inputValueFinal: string = inputValue.split(" ").join("+");
        const query = `q=${inputValueFinal}&type=${filtersQueryName[activeFilter]}`;
        let url = `spotify/search?${query}`;
        try {
            console.log(url);
            const response = await requests.sendRequest("GET", url);
            console.log(JSON.stringify(response, null, 2));
            const options = response.map((item) => {
                label: item.name;
                value: item.id;
            });
            callback(response);
        } catch (error) {
            console.error(error);
        }
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
                    onClick={() => setActiveFilter(0)}
                >
                    My Top Songs
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter(1)}
                >
                    Selected Artists
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter(2)}
                >
                    Selected Songs
                </Button>
                <Button
                    size="sm"
                    onClick={() => setActiveFilter(3)}
                >
                    Selected Genres
                </Button>
            </Group>
            <Stack>
                <Group>
                    <div className={classes.inputContainer}>
                        <h3>Choose {filters[activeFilter]}:</h3>
                        <AsyncSelect
                            cacheOptions
                            // loadOptions={loadOptions}
                            defaultOptions
                            styles={{
                                control: (baseStyles, state) => ({
                                    ...baseStyles,
                                    paddingLeft: "0.25rem",
                                    border: "none",
                                    marginTop: "0.5rem",
                                    backgroundColor: "var(--background-color-4)",
                                    borderRadius: "0.5rem",
                                }),
                            }}
                        />
                    </div>
                    <Stack className={classes.selectionViewContainer}>
                        <h3>Selected {filters[activeFilter]}:</h3>
                        <div className={classes.selectionElement}>
                            <Group>
                                <img
                                    className={classes.selectionElementPfp}
                                    src="https://i.scdn.co/image/ab676161000051746725802588d7dc1aba076ca5"
                                />
                                <p className={classes.elementText}>Ariana Grande</p>
                                <p className={cs(classes.elementText, classes.elementGenreText)}>Trap, Rage</p>
                                <IconX
                                    color="#3f3e3e" /* text-color-disabled */
                                    size={20}
                                    className={classes.removeIcon}
                                />
                            </Group>
                        </div>
                    </Stack>
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
