import Group from "../../atoms/Group/Group";
import Stack from "../../atoms/Stack/Stack";
import classes from "./StatsDisplay.module.css";
import cs from "classnames";
import { IconChartArrowsVertical } from "@tabler/icons-react";
import { IconThumbUpFilled } from "@tabler/icons-react";
import { IconThumbDownFilled } from "@tabler/icons-react";
interface StatsDisplayProps extends React.HTMLAttributes<HTMLDivElement> {}

const StatsDisplay = ({ children, className, ...props }: StatsDisplayProps): React.JSX.Element => {
    return (
        <div
            className={cs(classes.container, className)}
            {...props}
        >
            <div className={classes.statsContainer}>
                <Group>
                    <Stack>
                        <h1 className={classes.title}>User Stats</h1>
                        <h2 className={classes.categoryName}>Reactions</h2>
                        <Group>
                            <p className={classes.statText}>Songs liked: </p>
                            <IconThumbUpFilled color="#1ED760" />
                        </Group>
                        <Group>
                            <p className={classes.statText}>Songs disliked: </p>
                            <IconThumbDownFilled color="#DB2004" />
                        </Group>
                    </Stack>

                    <IconChartArrowsVertical
                        className={classes.statIcon}
                        size={280}
                    />
                </Group>
            </div>
        </div>
    );
};

export default StatsDisplay;
