import React, { useEffect, useState } from 'react';
const ngrokUrl = import.meta.env.VITE_NGROK_URL;
interface Artist {
  id: string;
  name: string;
}

const TopArtists: React.FC = () => {
  const [artists, setArtists] = useState<Artist[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopArtists = async () => {
      try {
        const res = await fetch(`${ngrokUrl}/api/auth/spotify/get-top-artists/`, { credentials: 'include' });
        if (!res.ok) throw new Error(`Błąd sieci: ${res.status}`);
        const data = await res.json();
        setArtists(data.top_artists);
      } catch (e) {
        setError((e as Error).message);
      }
    };
    fetchTopArtists();
  }, []);

  if (error) return <div>Błąd: {error}</div>;
  if (!artists) return <div>Ładowanie...</div>;

  return (
    <ul>
      {artists.map((artist) => (
        <li key={artist.id}>{artist.name}</li>
      ))}
    </ul>
  );
};

export default TopArtists;
