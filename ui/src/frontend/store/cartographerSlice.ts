import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';
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
  total: number;
  loading: boolean;
  error: string | null;
}


export const fetchCartographerList = createAuthThunk(
  'cartographer/fetchList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.Survey_Cartographer_list( { filter: undefined, position, count } ),
      contractor.Survey_Cartographer_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( c: any ) => ( {
      id: c.identifier,
      identifier: c.identifier,
      message: c.message ?? '',
      foundation: c.foundation?.toString() ?? '',
      last_checkin: dateStr( c.last_checkin ),
      created: dateStr( c.created ),
      updated: dateStr( c.updated ),
    } ) ) as CartographerItem[];
    return { items, total: listResult.total } as PagedResult<CartographerItem>;
  }
);

const cartographerSlice = createSlice( {
  name: 'cartographer',
  initialState: { list: null, total: 0, loading: false, error: null } as CartographerState,
  reducers: {
    invalidate: ( state ) => { state.list = null; state.total = 0; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchCartographerList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchCartographerList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload.items; state.total = action.payload.total; } )
      .addCase( fetchCartographerList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateCartographer } = cartographerSlice.actions;
export default cartographerSlice.reducer;
