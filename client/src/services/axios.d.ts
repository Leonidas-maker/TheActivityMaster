import "axios";

declare module "axios" {
  export interface AxiosRequestConfig {
    /**
     * If "true", the request will not be authenticated.
     */
    skipAuth?: boolean;
    /**
     * Is used internally for the token refresh mechanism.
     */
    _retry?: boolean;
  }
}