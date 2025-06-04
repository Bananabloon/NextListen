import Stack from "../../components/atoms/Stack/Stack";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
const DiscoveryPage = (): React.JSX.Element => {
    return (
        <Stack className={classes.container}>
            <SongCardConveyor className={classes.conveyor} />
            {/* <div id="test-y"></div> */}
        </Stack>
    );
};

export default DiscoveryPage;
