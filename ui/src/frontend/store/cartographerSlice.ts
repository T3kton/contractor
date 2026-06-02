import type { Contractor } from '../lib/Contractor';
import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import { dateStr } from '../lib/utils';

export interface CartographerItem {
  id: string;
  identifier: string;
  message: string;
  foundation: string;
  last_checkin: string;
  created: string;
  updated: string;
}

interface CartographerState {
  list: CartographerItem[] | null;
  loading: boolean;
  error: string | null;
}


export const fetchCartographerList = createAuthThunk(
  'cartographer/fetchList',
  async ( _: void, contractor ) =>
  {
    const result = await contractor.Survey_Cartographer_get_multi( { filter: undefined } );
    return Object.values( result ).map( ( c: any ) => ( {
      id: c.identifier,
      identifier: c.identifier,
      message: c.message ?? '',
      foundation: c.foundation?.toString() ?? '',
      last_checkin: dateStr( c.last_checkin ),
      created: dateStr( c.created ),
      updated: dateStr( c.updated ),
    } ) ) as CartographerItem[];
  }
);

const cartographerSlice = createSlice( {
  name: 'cartographer',
  initialState: { list: null, loading: false, error: null } as CartographerState,
  reducers: {
    invalidate: ( state ) => { state.list = null; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchCartographerList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchCartographerList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload; } )
      .addCase( fetchCartographerList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateCartographer } = cartographerSlice.actions;
export default cartographerSlice.reducer;
