import { Container, Title, Button, TextInput } from '@mantine/core';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function Home() {
  const [trackUrl, setTrackUrl] = useState('');
  const navigate = useNavigate();

  const handleSubmit = () => {
    navigate(`/results?url=${encodeURIComponent(trackUrl)}`);
  };

  return (
    <Container size="xs">
      <Title style={{ textAlign: "center" }} mt="xl">Wprowadź link do utworu</Title>
      <TextInput
        placeholder="https://open.spotify.com/track/..."
        value={trackUrl}
        onChange={(e) => setTrackUrl(e.currentTarget.value)}
        mt="md"
      />
      <Button fullWidth mt="md" onClick={handleSubmit}>Szukaj rekomendacji</Button>
    </Container>
  );
}
