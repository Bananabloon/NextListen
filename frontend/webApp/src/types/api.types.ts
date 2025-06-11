export type Feedback = -1 | 0 | 1;

export type DiscoveryType = "top" | "artist" | "genre" | "song";

export interface TrackDetails {
    album: string;
    album_cover: string;
    album_type: string;
    artists: string[];
    duration_ms: number;
    external_url: string;
    id: string;
    markets: string[];
    name: string;
    popularity: number;
    preview_url: null | string;
    release_date: string;
}

export interface GeneratedSong {
    artist: string;
    curveball: boolean;
    explicit: boolean;
    feedback_value: Feedback;
    title: string;
    track_details: TrackDetails;
    uri: string;
}

export interface GenerateFromTopOptions {
    count: number;
}

export interface GenerateFromArtistOptions {
    count: number;
    artists: string[];
}

export interface GenerateFromSongOptions {
    count: number;
    artists: string;
    title: string;
}

export interface GenerateFromGenreOptions {
    count: number;
    genre: string;
}

export type DiscoveryOptionsMap = {
    top: GenerateFromTopOptions;
    artist: GenerateFromArtistOptions;
    genre: GenerateFromGenreOptions;
    song: GenerateFromSongOptions;
};

export type DiscoveryState =
    | { type: "top"; options: GenerateFromTopOptions }
    | { type: "artist"; options: GenerateFromArtistOptions }
    | { type: "genre"; options: GenerateFromGenreOptions }
    | { type: "song"; options: GenerateFromSongOptions }
    | null;
