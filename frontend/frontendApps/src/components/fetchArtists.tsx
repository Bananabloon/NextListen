import React, { useEffect, useState } from 'react';

const ngrokUrl = import.meta.env.VITE_NGROK_URL;

interface Artist {
  id: string;
  name: string;
  images: { url: string }[];
}

const TopArtists: React.FC = () => {
  const [artists, setArtists] = useState<Artist[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopArtists = async () => {
      try {
        const res = await fetch(`${ngrokUrl}/api/spotify/top-artists/`, { credentials: 'include' });
        if (!res.ok) throw new Error(`Błąd sieci: ${res.status}`);
        const data = await res.json();
        setArtists(data.items); 
      } catch (e) {
        setError((e as Error).message);
      }
    };
    fetchTopArtists();
  }, []);

  if (error) return <div>Błąd: {error}</div>;
  if (!artists) return <div>Ładowanie...</div>;

  return (
    <ul className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {artists.map((artist) => (
        <li key={artist.id} className="flex flex-col items-center">
          <img
            src={artist.images?.[0]?.url || ''}
            alt={artist.name}
            className="w-32 h-32 rounded-full object-cover shadow-md"
          />
          <span className="mt-2 text-center">{artist.name}</span>
        </li>
      ))}
    </ul>
  );
};

export default TopArtists;
