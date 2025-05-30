import { IconUserCircle } from "@tabler/icons-react";
import classes from "./Avatar.module.css";
import cs from "classnames";
import React from "react";

interface AvatarProps {
    className?: string;
    src?: string;
    style?: any;
    size?: number;
}

const Avatar = ({ className, size = 24, src, style }: AvatarProps): React.JSX.Element => {
    return src ? (
        <img
            src={src}
            alt="Profile picture"
            aria-label="User's profile picture"
            className={cs(className, classes.profilePicture)}
            style={{
                height: `${size}px`,
                width: `${size}px`,
                ...style,
            }}
        />
    ) : (
        <IconUserCircle
            className={className}
            size={size}
            width={size}
            style={style}
            stroke={1.5}
        />
    );
};

export default Avatar;
