import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { AsyncThunk } from '@reduxjs/toolkit';
import type { Contractor } from '../lib/Contractor';
import { setAuthenticated, invalidateAll } from './appSlice';

export type CInPError = { msg: string; detail?: unknown };

// the CInP server defaults to Count=10 per list request when not specified; pass this to get_multi calls
// that are populating a bounded sub-list (e.g. the addresses inside one address block's detail view)
// where paging through the server on demand isn't worth the complexity.
export const FETCH_ALL_COUNT = 10000;

// default page size for top-level, server-paginated list views
export const DEFAULT_PAGE_SIZE = 25;

export interface PageParams {
  position: number;
  count: number;
}

export interface PagedResult<L> {
  items: L[];
  total: number;
}

const AUTH_ERROR_MSGS = new Set( [ 'Invalid Session', 'Not Authorized' ] );

export function createAuthThunk<Returned, ThunkArg = void>(
  typePrefix: string,
  payloadCreator: ( arg: ThunkArg, contractor: Contractor ) => Promise<Returned>
)
{
  return createAsyncThunk<Returned, ThunkArg, { extra: Contractor; rejectValue: CInPError }>(
    typePrefix,
    async ( arg, thunkAPI ) =>
    {
      try
      {
        return await payloadCreator( arg, thunkAPI.extra );
      }
      catch ( err: unknown )
      {
        const e = err as Record<string, unknown>;
        const cinpErr: CInPError = { msg: typeof e?.msg === 'string' ? e.msg : String( err ), detail: e?.detail };
        if ( AUTH_ERROR_MSGS.has( cinpErr.msg ) )
        {
          thunkAPI.dispatch( setAuthenticated( false ) );
        }
        return thunkAPI.rejectWithValue( cinpErr );
      }
    },
    {
      condition: ( _arg, { getState } ) =>
      {
        const state = getState() as { app: { authenticated: boolean } };
        return state.app.authenticated;
      },
    }
  );
}


interface PagedListState<L, D> {
  list: L[] | null;
  total: number;
  detail: D | null;
  loading: boolean;
  error: string | null;
}

type AuthThunk<T, A> = AsyncThunk<T, A, { extra: Contractor; rejectValue: CInPError }>;

// list is fetched a page (PageParams.count) at a time from the server, driven by total for TablePagination
export function createPagedListSlice<L, D>( config: {
  name: string;
  fetchList: AuthThunk<PagedResult<L>, any>;
  fetchOne: AuthThunk<D, any>;
} )
{
  return createSlice( {
    name: config.name,
    initialState: { list: null, total: 0, detail: null, loading: false, error: null } as PagedListState<L, D>,
    reducers: {
      invalidate: ( state ) => { state.list = null; state.total = 0; state.detail = null; },
    },
    extraReducers: ( builder ) =>
    {
      builder
        .addCase( config.fetchList.pending, ( state ) => { state.loading = true; state.error = null; } )
        .addCase( config.fetchList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload.items as any; state.total = action.payload.total; } )
        .addCase( config.fetchList.rejected, ( state, action ) => { state.loading = false; state.error = action.payload?.msg ?? action.error?.message ?? 'Error loading data'; } )
        .addCase( config.fetchOne.pending, ( state ) => { state.loading = true; state.error = null; } )
        .addCase( config.fetchOne.fulfilled, ( state, action ) => { state.loading = false; state.detail = action.payload as any; } )
        .addCase( config.fetchOne.rejected, ( state, action ) => { state.loading = false; state.error = action.payload?.msg ?? action.error?.message ?? 'Error loading data'; } )
        .addCase( invalidateAll, ( state ) => { state.list = null; state.total = 0; state.detail = null; state.loading = false; state.error = null; } );
    },
  } );
}
