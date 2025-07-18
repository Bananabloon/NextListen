import classes from "./ScrollingText.module.css";
import { useElementSize } from "@mantine/hooks";
import { useEffect, useState } from "react";

// speed is in pixels per second
const ScrollingText = ({ children, scroll = true, speed = 20, ...props }): React.JSX.Element => {
    const { width: containerWidth, ref: containerRef } = useElementSize();
    const { width: textWidth, ref: textRef } = useElementSize();
    const [shouldScroll, setShouldScroll] = useState(false);

    useEffect(() => {
        setShouldScroll(scroll && containerWidth > 0 && textWidth > 0 && textWidth > containerWidth);
    }, [scroll, textWidth, containerWidth]);

    return (
        <div
            className={classes.container}
            ref={containerRef}
            {...props}
        >
            <div
                className={`${classes.text} ${shouldScroll ? classes.scrolling : classes.notScrolling}`}
                style={{
                    animationDuration: `${textWidth / speed}s`,
                }}
            >
                <div ref={textRef}>{children}</div>
                {shouldScroll && (
                    <>
                        <div className={classes.spacer} />
                        <div>{children}</div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ScrollingText;
