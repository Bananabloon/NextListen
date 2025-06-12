export type Feedback = -1 | 0 | 1;

export type DiscoveryType = "top" | "artists" | "genres" | "tracks";
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
    curveball: boolean;
    explicit: boolean;
    feedback_value: Feedback;
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

export interface GenerateFromTrackOptions {
    count: number;
    titles: string[];
}

export interface GenerateFromGenreOptions {
    count: number;
    genre: string;
}

export type DiscoveryOptionsMap = {
    top: GenerateFromTopOptions;
    artists: GenerateFromArtistOptions;
    genres: GenerateFromGenreOptions;
    tracks: GenerateFromTrackOptions;
};

export type DiscoveryState =
    | { type: "top"; options: GenerateFromTopOptions }
    | { type: "artists"; options: GenerateFromArtistOptions }
    | { type: "genres"; options: GenerateFromGenreOptions }
    | { type: "tracks"; options: GenerateFromTrackOptions }
    | null;
