// frontend/src/components/UserDashboard.js
import React, { useState, useEffect } from 'react';
import { getUserProfile, getUserVehicles } from '../services/api';

const UserDashboard = () => {
  const [profile, setProfile] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const profileData = await getUserProfile();
        const vehiclesData = await getUserVehicles();
        
        setProfile(profileData);
        setVehicles(vehiclesData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching user data:', error);
        setLoading(false);
      }
    };
    
    fetchUserData();
  }, []);
  
  if (loading) return <div>Loading profile data...</div>;
  
  return (
    <div className="dashboard">
      <div className="profile-section">
        <h2>Welcome, {profile?.user?.first_name || profile?.user?.username}</h2>
        {profile?.profile_image && (
          <img 
            src={profile.profile_image} 
            alt="Profile" 
            className="profile-image" 
          />
        )}
      </div>
      
      <div className="vehicles-section">
        <h3>Your Vehicles</h3>
        {vehicles.length === 0 ? (
          <p>No vehicles added yet. Add your first vehicle to start tracking.</p>
        ) : (
          vehicles.map(vehicle => (
            <div key={vehicle.id} className="vehicle-card">
              <h4>{vehicle.nickname || `${vehicle.car_details.brand_name} ${vehicle.car_details.model}`}</h4>
              <p>Year: {vehicle.car_details.year}</p>
              <p>License Plate: {vehicle.license_plate}</p>
              {vehicle.is_primary && <span className="primary-badge">Primary</span>}
              <div className="vehicle-actions">
                <button className="btn btn-sm btn-primary">View Details</button>
                <button className="btn btn-sm btn-success">Scan OBD Codes</button>
                <button className="btn btn-sm btn-info">Maintenance History</button>
              </div>
            </div>
          ))
        )}
        <button className="btn btn-primary mt-3">Add New Vehicle</button>
      </div>
    </div>
  );
};

export default UserDashboard;