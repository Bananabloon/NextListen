import { GridLoader } from "react-spinners";
import Stack from "../../atoms/Stack/Stack";
import SongCardPlaceholder, { SongCardPlaceholderProps } from "./SongCardPlaceholder";

const SongCardLoading = (props: SongCardPlaceholderProps): React.JSX.Element => {
    return (
        <SongCardPlaceholder>
            <Stack
                style={{
                    height: "100%",
                    alignItems: "center",
                    justifyContent: "center",
                }}
            >
                <GridLoader color="white" />
                <span style={{ fontSize: "var(--font-size-lg)", fontWeight: "600" }}>Generating more...</span>
            </Stack>
        </SongCardPlaceholder>
    );
};

export default SongCardLoading;
