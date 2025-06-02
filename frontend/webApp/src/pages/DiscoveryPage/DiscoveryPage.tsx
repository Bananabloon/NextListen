import { useEffect } from "react";
import useFetch from "../../hooks/useFetch";
import useRequests from "../../hooks/useRequests";
import Stack from "../../components/atoms/Stack/Stack";
import Group from "../../components/atoms/Group/Group";

const DiscoveryPage = (): React.JSX.Element => {
    const { data } = useFetch("/spotify/top-artists/");

    console.log();

    return (
        <Group>
            {data &&
                data.items.map((item, i) => (
                    <Stack
                        style={{ height: "100px" }}
                        key={i}
                    >
                        <img
                            src={item.images?.[2]?.url}
                            key={i}
                            style={{ width: 75, aspectRatio: "1/1" }}
                        />
                        {item.name}
                    </Stack>
                ))}
        </Group>
    );
};

export default DiscoveryPage;
