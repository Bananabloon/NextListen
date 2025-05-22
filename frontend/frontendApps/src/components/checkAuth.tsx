// CheckAuth.tsx
import React, { useEffect } from 'react';

const CheckAuth: React.FC = () => {
    useEffect(() => {
    fetch('https://localhost/api/auth/spotify/ProtectedView/', {
        method: 'GET',
        credentials: 'include',
        headers: {
        'Content-Type': 'application/json',
        },
    })
    .then(async (response) => {
        console.log('Status:', response.status);
        const text = await response.text();  // najpierw tekst
        console.log('Response text:', text);

        try {
        const data = JSON.parse(text);
        console.log('Authenticated user data:', data);
        } catch (e) {
        console.error('JSON parse error:', e);
        throw new Error('Response is not valid JSON');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
    }, []);


  return <div>Checking auth... open console to see results.</div>;
};

export default CheckAuth;
