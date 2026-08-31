import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const API_URL = 'http://localhost:8000';

function ClickHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
}

function App() {
  const [points, setPoints] = useState([]);
  const [nearbyResults, setNearbyResults] = useState([]);
  const [searchCenter, setSearchCenter] = useState(null);
  const [bufferGeoJson, setBufferGeoJson] = useState(null);
  const radius = 1000;

  useEffect(() => {
    fetch(`${API_URL}/points`)
      .then((res) => res.json())
      .then((data) => setPoints(data))
      .catch((err) => console.error('Erreur de chargement des points:', err));
  }, []);

  const handleMapClick = async (latlng) => {
    setSearchCenter(latlng);
    setBufferGeoJson(null);
    try {
      const res = await fetch(
        `${API_URL}/points/nearby?latitude=${latlng.lat}&longitude=${latlng.lng}&radius_meters=${radius}`
      );
      const data = await res.json();
      setNearbyResults(data);
    } catch (err) {
      console.error('Erreur de recherche nearby:', err);
    }
  };

  const handleShowBuffer = async () => {
    if (!searchCenter) return;
    try {
      const res = await fetch(
        `${API_URL}/zones/buffer?latitude=${searchCenter.lat}&longitude=${searchCenter.lng}&radius_meters=${radius}`
      );
      const data = await res.json();
      setBufferGeoJson(JSON.parse(data.geojson));
    } catch (err) {
      console.error('Erreur de récupération du buffer:', err);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative' }}>
      {searchCenter && (
        <button
          onClick={handleShowBuffer}
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            zIndex: 1000,
            padding: '8px 16px',
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: 4,
            cursor: 'pointer',
          }}
        >
          Afficher la zone tampon
        </button>
      )}

      <MapContainer center={[48.8566, 2.3522]} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        <ClickHandler onMapClick={handleMapClick} />

        {points.map((point) => (
          <Marker key={point.id} position={[point.latitude, point.longitude]}>
            <Popup>
              {point.name}
              {nearbyResults.some((r) => r.id === point.id) && ' — dans le rayon !'}
            </Popup>
          </Marker>
        ))}

       

        {bufferGeoJson && (
          <GeoJSON data={bufferGeoJson} pathOptions={{ color: 'green', fillOpacity: 0.2 }} />
        )}
      </MapContainer>
    </div>
  );
}

export default App;