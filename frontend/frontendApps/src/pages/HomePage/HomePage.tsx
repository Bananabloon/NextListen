import Button from "../../components/atoms/Button/Button";
import Stack from "../../components/atoms/Stack/Stack";

const HomePage = (): React.JSX.Element => {
    return (
        <Stack>
            <Button size="xs">Button xs test</Button>
            <Button size="sm">Button sm test</Button>
            <Button size="md">Button md test</Button>
            <Button size="lg">Button lg test</Button>
            <Button size="xl">Button xl test</Button>
        </Stack>
    );
};

export default HomePage;
