export const formatTime = (ms: number): string => {
    const timeInSeconds = Math.floor(ms / 1000);

    const hours = Math.floor(timeInSeconds / 3600);
    const minutes = Math.floor((timeInSeconds % 3600) / 60);
    const secs = timeInSeconds % 60;

    const pad = (num: number): string => num.toString().padStart(2, "0");

    return `${hours ? `${pad(hours)}:` : ""}${pad(minutes)}:${pad(secs)}`;
};
