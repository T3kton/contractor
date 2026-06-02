import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  authenticated: boolean;
  serverError: { msg: string; trace: string } | null;
}

const appSlice = createSlice( {
  name: 'app',
  initialState: { authenticated: false, serverError: null } as AppState,
  reducers: {
    setAuthenticated: ( state, action: PayloadAction<boolean> ) => { state.authenticated = action.payload; },
    showServerError: ( state, action: PayloadAction<{ msg: string; trace?: string }> ) =>
    {
      state.serverError = { msg: action.payload.msg, trace: action.payload.trace ?? '' };
    },
    clearServerError: ( state ) => { state.serverError = null; },
    invalidateAll: () => {},
  },
} );

export const { setAuthenticated, showServerError, clearServerError, invalidateAll } = appSlice.actions;
export default appSlice.reducer;
