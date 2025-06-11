import classes from "./FilteredSelect.module.css";
import cs from "classnames";
import useRequests from "../../../hooks/useRequests";
import { useDebouncedCallback } from "@mantine/hooks";
import Select from "react-select";
import { useState } from "react";
import "./FilteredSelect.css";
interface ItemFilterContainerProps extends React.HTMLAttributes<HTMLDivElement> {
    filter: "artists" | "tracks" | "genres";
    changeSelectOption: Function;
}
const requests = useRequests();
type OptionType = {
    label: string;
    value: string;
};

const FilteredSelect = ({
    changeSelectOption,
    filter,
    children,
    className,
    ...props
}: ItemFilterContainerProps): React.JSX.Element => {
    const [options, setOptions] = useState<OptionType[]>([]);
    const [value, setValue] = useState(null);
    const [items, setItems] = useState<any[]>([]);

    const search = async (inputValue: string) => {
        if (!inputValue) return;
        const inputValueFinal: string = inputValue.split(" ").join("+");
        const query = `q=${inputValueFinal}&type=${filter.slice(0, -1)}`;
        let url = `spotify/search?${query}`;

        try {
            const response = await requests.sendRequest("GET", url);
            setItems(response[filter].items);
            setOptions(
                response[filter].items.map((item) => {
                    return {
                        label: item.name,
                        value: item.uri,
                    };
                })
            );
        } catch (error) {
            console.error(error);
        }
    };

    const debouncedSearch = useDebouncedCallback(search, 400);
    const handleOptionChange = (selectedOption) => {
        const selectedItem = items.find((item) => item.uri === selectedOption.value);
        changeSelectOption(selectedItem);
        setValue(null);
    };

    return (
        <div
            className={cs(classes.inputContainer, className)}
            {...props}
        >
            <h3>Choose {filter}:</h3>
            <Select
                value={value}
                className="filteredSelectContainer"
                classNamePrefix="filteredSelect"
                unstyled
                onInputChange={(inputValue) => debouncedSearch(inputValue)}
                onChange={handleOptionChange}
                onMenuClose={() => setOptions([])}
                options={options}
                placeholder="Enter an artist name to select"
                noOptionsMessage={({ inputValue }) => (inputValue === "" ? "" : "Looking for matches...")}
                styles={{
                    control: (baseStyles, state) => ({
                        ...baseStyles,
                        paddingLeft: "var(--spacing-sm)",
                        marginTop: "var(--spacing-sm)",
                        backgroundColor: "var(--background-color-4)",
                        borderRadius: "var(--radius-sm)",
                        borderBottomLeftRadius: state.menuIsOpen ? "0px" : "var(--spacing-sm)",
                        borderBottomRightRadius: state.menuIsOpen ? "0px" : "var(--spacing-sm)",
                    }),
                }}
            />
        </div>
    );
};

export default FilteredSelect;

