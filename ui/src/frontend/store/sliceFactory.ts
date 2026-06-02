import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { AsyncThunk } from '@reduxjs/toolkit';
import type { Contractor } from '../lib/Contractor';
import { setAuthenticated, invalidateAll } from './appSlice';

export type CInPError = { msg: string; detail?: unknown };

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


interface DetailListState<L, D> {
  list: L[] | null;
  detail: D | null;
  loading: boolean;
  error: string | null;
}

type AuthThunk<T, A> = AsyncThunk<T, A, { extra: Contractor; rejectValue: CInPError }>;

export function createDetailListSlice<L, D>( config: {
  name: string;
  fetchList: AuthThunk<L[], any>;
  fetchOne: AuthThunk<D, any>;
} )
{
  return createSlice( {
    name: config.name,
    initialState: { list: null, detail: null, loading: false, error: null } as DetailListState<L, D>,
    reducers: {
      invalidate: ( state ) => { state.list = null; state.detail = null; },
    },
    extraReducers: ( builder ) =>
    {
      builder
        .addCase( config.fetchList.pending, ( state ) => { state.loading = true; state.error = null; } )
        .addCase( config.fetchList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload as any; } )
        .addCase( config.fetchList.rejected, ( state, action ) => { state.loading = false; state.error = action.payload?.msg ?? action.error?.message ?? 'Error loading data'; } )
        .addCase( config.fetchOne.pending, ( state ) => { state.loading = true; state.error = null; } )
        .addCase( config.fetchOne.fulfilled, ( state, action ) => { state.loading = false; state.detail = action.payload as any; } )
        .addCase( config.fetchOne.rejected, ( state, action ) => { state.loading = false; state.error = action.payload?.msg ?? action.error?.message ?? 'Error loading data'; } )
        .addCase( invalidateAll, ( state ) => { state.list = null; state.detail = null; state.loading = false; state.error = null; } );
    },
  } );
}
