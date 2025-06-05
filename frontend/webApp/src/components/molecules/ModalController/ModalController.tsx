import { useEffect, useRef, useState } from "react";
import classes from "./QueueGenerateOverlay.module.css";
import Portal from "../../atoms/Portal/Portal";
import Button from "../../atoms/Button/Button";

interface QueueGenerateOverlayProps extends React.HTMLAttributes<HTMLDivElement> {}

const QueueGenerateOverlay = ({ children, className, ...props }: QueueGenerateOverlayProps): React.JSX.Element => {
    const [show, setShow] = useState(false);
    const ref = useRef(null);

    const inboundEventListener = (e: MouseEvent) => {
        const element = ref.current! as HTMLDialogElement;
        if (element.open) {
            let modalPos = element.getBoundingClientRect();
            if (
                e.clientX < modalPos.left ||
                e.clientY < modalPos.top ||
                e.clientX > modalPos.right ||
                e.clientY > modalPos.bottom
            ) {
                element.style.opacity = "0";
                element.close();
            }
        }
    };

    useEffect(() => {
        window.addEventListener("click", inboundEventListener);
        return () => {
            window.removeEventListener("click", inboundEventListener);
        };
    }, []);

    return (
        <>
            <Portal>
                <dialog
                    ref={ref}
                    className={classes.container}
                    style={{ width: `${width}px`, height: `${height}px` }}
                >
                    {children}
                </dialog>
            </Portal>
            <Button
                size="md"
                variant="default"
                className={classes.generateQueueButton}
                onClick={(e) => {
                    e.stopPropagation();
                    const element = ref.current! as HTMLDialogElement;
                    element.showModal();
                    element.style.opacity = "1";
                }}
            >
                {buttonText}
            </Button>
        </>
    );
};

export default ModalController;
