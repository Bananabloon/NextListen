export type Feedback = -1 | 0 | 1;

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
