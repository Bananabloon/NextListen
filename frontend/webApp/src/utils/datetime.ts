export const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    const pad = (num: number): string => num.toString().padStart(2, "0");

    return `${hours ? `${pad(hours)}:` : ""}${pad(minutes)}:${pad(secs)}`;
};
