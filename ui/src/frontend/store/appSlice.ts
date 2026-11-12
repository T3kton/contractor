import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  authenticated: boolean;
  serverError: { msg: string; trace: string } | null;
  updateVersion: number;
}

const appSlice = createSlice( {
  name: 'app',
  initialState: { authenticated: false, serverError: null, updateVersion: 0 } as AppState,
  reducers: {
    setAuthenticated: ( state, action: PayloadAction<boolean> ) => { state.authenticated = action.payload; },
    showServerError: ( state, action: PayloadAction<{ msg: string; trace?: string }> ) =>
    {
      state.serverError = { msg: action.payload.msg, trace: action.payload.trace ?? '' };
    },
    clearServerError: ( state ) => { state.serverError = null; },
    invalidateAll: ( state ) => { state.updateVersion += 1; },
  },
} );

export const { setAuthenticated, showServerError, clearServerError, invalidateAll } = appSlice.actions;
export default appSlice.reducer;
