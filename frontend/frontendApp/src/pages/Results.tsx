import { useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Container, Title } from '@mantine/core';

export function Results() {
  const { search } = useLocation();
  const url = new URLSearchParams(search).get('url');
  const [features, setFeatures] = useState<any>(null);

  useEffect(() => {
    if (!url) return;

    fetch(`http://localhost:3000/api/analyze?url=${encodeURIComponent(url)}`)
      .then((res) => res.json())
      .then((data) => setFeatures(data));
  }, [url]);

  return (
    <Container>
      <Title>Wyniki dla utworu</Title>
      {features ? <pre>{JSON.stringify(features, null, 2)}</pre> : 'Ładowanie...'}
    </Container>
  );
}
