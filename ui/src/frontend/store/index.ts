import { configureStore } from '@reduxjs/toolkit';
import { Contractor } from '../lib/Contractor';
import appReducer from './appSlice';
import sitesReducer from './sitesSlice';
import plotsReducer from './plotsSlice';
import networksReducer from './networksSlice';
import blueprintsReducer from './blueprintsSlice';
import pxeReducer from './pxeSlice';
import foundationsReducer from './foundationsSlice';
import dependenciesReducer from './dependenciesSlice';
import structuresReducer from './structuresSlice';
import complexesReducer from './complexesSlice';
import addressBlocksReducer from './addressBlocksSlice';
import directoryReducer from './directorySlice';
import jobsReducer from './jobsSlice';
import jobLogReducer from './jobLogSlice';
import cartographerReducer from './cartographerSlice';
import todoReducer from './todoSlice';
import siteGraphReducer from './siteGraphSlice';

declare global {
  interface Window { API_BASE_URI: string; }
}

export const contractor = new Contractor( window.API_BASE_URI );

export const store = configureStore( {
  reducer: {
    app: appReducer,
    sites: sitesReducer,
    plots: plotsReducer,
    networks: networksReducer,
    blueprints: blueprintsReducer,
    pxe: pxeReducer,
    foundations: foundationsReducer,
    dependencies: dependenciesReducer,
    structures: structuresReducer,
    complexes: complexesReducer,
    addressBlocks: addressBlocksReducer,
    directory: directoryReducer,
    jobs: jobsReducer,
    jobLog: jobLogReducer,
    cartographer: cartographerReducer,
    todo: todoReducer,
    siteGraph: siteGraphReducer,
  },
  middleware: ( getDefaultMiddleware ) =>
    getDefaultMiddleware( {
      thunk: { extraArgument: contractor },
      serializableCheck: false,
    } ),
} );

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
