import React, { createContext, useState, useContext } from 'react';

// Define the shape of the Club context.
interface ClubContextType {
  clubId: string | null;
  setClubId: (clubId: string | null) => void;
}

// Create the context with default values.
const ClubContext = createContext<ClubContextType>({
  clubId: null,
  setClubId: () => {},
});

export const ClubProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [clubId, setClubId] = useState<string | null>(null);
  return (
    <ClubContext.Provider value={{ clubId, setClubId }}>
      {children}
    </ClubContext.Provider>
  );
};

// Custom hook to access the ClubContext.
export const useClubContext = () => useContext(ClubContext);