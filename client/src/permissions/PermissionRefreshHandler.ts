// This file defines a global callback for refreshing permissions when a 403 error occurs.

let permissionRefreshCallback: (() => void) | null = null;

// Register the global permission refresh callback.
export const setPermissionRefreshCallback = (cb: () => void) => {
  permissionRefreshCallback = cb;
};

// Trigger the callback if it is set.
export const triggerPermissionRefresh = () => {
  if (permissionRefreshCallback) {
    permissionRefreshCallback();
  }
};