import { useDebouncedCallback } from "@mantine/hooks";
import { useState } from "react";
import Select from "react-select";
import useRequests from "../../../hooks/useRequests";
import Stack from "../../atoms/Stack/Stack";
import classes from "./FilteredSelect.module.css";
import cs from "classnames";
import "./FilteredSelect.css";
import { ClipLoader } from "react-spinners";

interface ItemFilterContainerProps extends React.HTMLAttributes<HTMLDivElement> {
    filter: "top" | "artists" | "tracks" | "genres";
    changeSelectOption: Function;
}

type OptionType = {
    label: string;
    value: string;
};

const FilteredSelect = ({ changeSelectOption, filter, children, className, ...props }: ItemFilterContainerProps): React.JSX.Element => {
    const [options, setOptions] = useState<OptionType[]>([]);
    const [items, setItems] = useState<any[]>([]);
    const [value, setValue] = useState(null);

    const { sendRequest } = useRequests();

    const debouncedSearch = useDebouncedCallback(async (inputValue: string) => {
        if (!inputValue) {
            return;
        }

        const preparedValue = inputValue.split(" ").join("+");
        const type = filter.slice(0, -1); // remove pluralization
        const query = `q=${preparedValue}&type=${type}`;
        const url = `spotify/search?${query}`;

        return await sendRequest("GET", url)
            .then((data) => {
                const newItems = data[filter]?.items ?? [];
                setItems(newItems);
                setOptions(newItems.map((item) => ({ label: item.name, value: item.uri })));
            })
            .catch((err) => console.error(err));
    }, 400);

    const handleSelect = (selectedOption) => {
        const selectedItem = items.find((item) => item.uri === selectedOption.value);
        changeSelectOption(selectedItem);
        setValue(null);
    };

    return (
        filter !== "top" ? <Stack
            className={cs(classes.inputContainer, className)}
            {...props}
        >
            <p className={classes.label}>Choose {filter}:</p>
            <Select
                value={value}
                className="filteredSelectContainer"
                classNamePrefix="filteredSelect"
                unstyled
                onInputChange={(inputValue) => debouncedSearch(inputValue)}
                onChange={handleSelect}
                onMenuClose={() => setOptions([])}
                options={options}
                placeholder={`Enter your choice`}
                noOptionsMessage={({ inputValue }) =>
                    inputValue ? (
                        <>
                            <ClipLoader
                                size="14px"
                                color="var(--text-color-dimmed)"
                            />
                            Looking for matches...
                        </>
                    ) : (
                        <></>
                    )
                }
                styles={{
                    control: (baseStyles, state) => ({
                        ...baseStyles,
                        borderBottomLeftRadius: state.menuIsOpen ? "0px" : "var(--spacing-sm)",
                        borderBottomRightRadius: state.menuIsOpen ? "0px" : "var(--spacing-sm)",
                    }),
                }}
                classNames={{
                    noOptionsMessage: (_) => "filteredSelect__noOptionsMessage",
                }}
            />
        </Stack> : <h2>Generation based on your top songs.</h2>
    );
};

export default FilteredSelect;
