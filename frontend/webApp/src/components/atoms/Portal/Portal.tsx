import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

interface PortalProps {
    children: React.ReactNode;
}

const Portal = ({ children }: PortalProps) => {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    return createPortal(children, document.body);
};

export default Portal;
