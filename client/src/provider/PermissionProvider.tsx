import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { getSelfClubRole } from "@/src/services/club/employeeService";
import { useClubContext } from "./ClubProvider";
import { setPermissionRefreshCallback } from "@/src/permissions/PermissionRefreshHandler";
import { useAuth } from "@/src/provider/AuthContextProvider";

// Define the structure of a permission.
interface Permission {
    name: string;
    description: string;
}

// Define the structure of the self club role returned by the API.
interface SelfClubRole {
    id: number;
    level: number;
    name: string;
    description: string;
    permissions: Permission[];
}

// Define the shape of our Permission context.
interface PermissionContextType {
    permissions: string[];
    hasPermission: (perm: string) => boolean;
    refreshPermissions: () => Promise<void>;
}

// Create the context with default values.
const PermissionContext = createContext<PermissionContextType>({
    permissions: [],
    hasPermission: () => false,
    refreshPermissions: async () => { },
});

export const PermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // Get the current club ID from ClubContext.
    const { clubId } = useClubContext();
    // Get auth state from AuthContext.
    const { authState } = useAuth();
    const [permissions, setPermissions] = useState<string[]>([]);
    const lastFetchedRef = useRef<number>(0);

    // Function to refresh permissions from the API.
    const refreshPermissions = useCallback(async (force: boolean = false) => {
        if (!clubId) {
            setPermissions([]);
            return;
        }
        const now = Date.now();
        // If not forcing and the permissions were fetched within the last 5 minutes, do not refresh.
        if (!force && now - lastFetchedRef.current < 300000) {
            return;
        }
        try {
            const data: SelfClubRole = await getSelfClubRole(clubId);
            let permNames = data.permissions.map((perm: Permission) => perm.name);
            // If the role level is 0, add the "club_owner" permission
            if (data.level === 0 && !permNames.includes("club_owner")) {
                permNames.push("club_owner");
            }
            setPermissions(permNames);
            lastFetchedRef.current = now;
        } catch (error) {
            console.error("Failed to refresh permissions", error);
        }
    }, [clubId]);

    // When clubId changes, force a refresh.
    useEffect(() => {
        lastFetchedRef.current = 0; // Reset lastFetchedRef when clubId changes
        refreshPermissions();
    }, [clubId, refreshPermissions]);

    // Clear permissions when the user logs out.
    useEffect(() => {
        if (!authState.isLoggedIn) {
            setPermissions([]);
            lastFetchedRef.current = 0;
        }
    }, [authState.isLoggedIn]);

    // Register the global permission refresh callback for 403 errors.
    useEffect(() => {
        // Register a callback that forces a permissions refresh when triggered (e.g., on a 403 error)
        setPermissionRefreshCallback(() => refreshPermissions(true));
        return () => {
            setPermissionRefreshCallback(() => { });
        };
    }, [refreshPermissions]);

    // Set up an interval to refresh permissions every 5 minutes.
    useEffect(() => {
        const interval = setInterval(() => {
            refreshPermissions();
        }, 300000);
        return () => clearInterval(interval);
    }, [refreshPermissions]);

    // Helper function to check for a permission.
    const hasPermission = (perm: string) => permissions.includes(perm);

    return (
        <PermissionContext.Provider value={{ permissions, hasPermission, refreshPermissions }}>
            {children}
        </PermissionContext.Provider>
    );
};

// Custom hook to use the PermissionContext.
export const usePermissionContext = () => useContext(PermissionContext);