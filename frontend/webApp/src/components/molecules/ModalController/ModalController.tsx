import React, { forwardRef, PropsWithChildren, useEffect, useImperativeHandle, useRef } from "react";
import classes from "./ModalController.module.css";
import Portal from "../../atoms/Portal/Portal";
import Button, { ButtonProps } from "../../atoms/Button/Button";
import cs from "classnames";
import IconButton from "../../atoms/IconButton/IconButton";
import { IconX } from "@tabler/icons-react";

export interface ModalControllerHandle {
    open: () => void;
    close: () => void;
}

export interface ModalControllerProps extends React.HTMLAttributes<HTMLDialogElement> {
    width: number;
    height: number;
    buttonProps?: ButtonProps;
    buttonContent?: React.ReactNode;
    onClose?: () => void;
}

const ModalController = forwardRef<ModalControllerHandle, ModalControllerProps>(
    ({ width, height, buttonProps, buttonContent, children, className, onClose, ...props }, ref): React.JSX.Element => {
        const dialogRef = useRef<HTMLDialogElement>(null);

        // opens the modal
        const open = (e) => {
            const element = dialogRef.current! as HTMLDialogElement;
            e.stopPropagation();
            element.showModal();
            element.style.opacity = "1";
        };

        // does not close the modal, it fires ON closing
        const handleClose = () => {
            const element = dialogRef.current! as HTMLDialogElement;
            element.style.opacity = "0";
            onClose?.();
        };

        const inboundEventListener = (e: MouseEvent) => {
            const element = dialogRef.current! as HTMLDialogElement;
            const rect = element.getBoundingClientRect();
            const clickedOutside = e.clientX < rect.left || e.clientY < rect.top || e.clientX > rect.right || e.clientY > rect.bottom;

            if (!element.open || !clickedOutside) return;

            element.close();
        };

        useImperativeHandle(ref, () => ({
            open: () => (dialogRef.current! as HTMLDialogElement).showModal(),
            close: () => (dialogRef.current! as HTMLDialogElement).close(),
        }));

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
                        ref={dialogRef}
                        onClose={handleClose}
                        className={cs(classes.container, className)}
                        style={{ width, height }}
                        {...props}
                    >
                        <IconButton
                            onClick={() => dialogRef.current?.close()}
                            className={classes.closeButton}
                            variant="transparent"
                        >
                            <IconX />
                        </IconButton>
                        {children}
                    </dialog>
                </Portal>
                {buttonContent && (
                    <Button
                        size="md"
                        variant="default"
                        onClick={open}
                        {...buttonProps}
                        className={cs(classes.generateQueueButton, buttonProps?.className)}
                    >
                        {buttonContent}
                    </Button>
                )}
            </>
        );
    }
);

export default ModalController;
