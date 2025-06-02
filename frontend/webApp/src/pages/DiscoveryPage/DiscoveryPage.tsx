import { useEffect } from "react";
import useFetch from "../../hooks/useFetch";
import useRequests from "../../hooks/useRequests";
import Stack from "../../components/atoms/Stack/Stack";
import Group from "../../components/atoms/Group/Group";
import SongCardConveyor from "../../components/organisms/SongCardConveyor/SongCardConveyor";
import classes from "./DiscoveryPage.module.css";
const DiscoveryPage = (): React.JSX.Element => {
    const { data } = useFetch("/spotify/top-artists/");

    console.log();

    return (
        <Stack className={classes.container}>
            <SongCardConveyor className={classes.conveyor} />
        </Stack>
    );
};

export default DiscoveryPage;
