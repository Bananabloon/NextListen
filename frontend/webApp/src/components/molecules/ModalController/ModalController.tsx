import { useEffect, useRef } from "react";
import classes from "./ModalController.module.css";
import Portal from "../../atoms/Portal/Portal";
import Button from "../../atoms/Button/Button";
import cs from "classnames";

interface ModalControllerProps extends React.HTMLAttributes<HTMLDivElement> {
    width: number;
    height: number;
    buttonText: string;
}

const ModalController = ({ width, height, buttonText, children, className, ...props }: ModalControllerProps): React.JSX.Element => {
    const ref = useRef(null);

    const inboundEventListener = (e: MouseEvent) => {
        const element = ref.current! as HTMLDialogElement;
        if (element.open) {
            let modalPos = element.getBoundingClientRect();
            if (e.clientX < modalPos.left || e.clientY < modalPos.top || e.clientX > modalPos.right || e.clientY > modalPos.bottom) {
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
                    className={cs(classes.container, className)}
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
