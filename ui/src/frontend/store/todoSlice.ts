import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import { Contractor, Site_Site, Building_Foundation } from '../lib/Contractor';
import { dateStr } from '../lib/utils';

export interface TodoFoundationItem {
  id: string;
  locator: string;
  dependencyCount: string;
  complex: string;
  created: string;
  updated: string;
}

interface TodoState {
  list: TodoFoundationItem[] | null;
  classList: string[] | null;
  loading: boolean;
  error: string | null;
}


export const fetchFoundationClassList = createAuthThunk(
  'todo/fetchClassList',
  async ( _: void, contractor ) =>
  {
    return await contractor.Building_Foundation_call_getFoundationTypes() as string[];
  }
);

export const fetchTodoList = createAuthThunk(
  'todo/fetchList',
  async ( { site, hasDependancies, foundationClass }: { site: string; hasDependancies: boolean; foundationClass: string | null }, contractor ) =>
  {
    const filter = site
      ? new Building_Foundation._ListFilter_todo( new Site_Site( contractor, site ), hasDependancies, foundationClass || '' )
      : undefined;
    const result = await contractor.Building_Foundation_get_multi( { filter } );
    return Object.values( result ).map( ( f: any ) => ( {
      id: f.locator,
      locator: f.locator,
      dependencyCount: ' ',
      complex: ' ',
      created: dateStr( f.created ),
      updated: dateStr( f.updated ),
    } ) ) as TodoFoundationItem[];
  }
);

const todoSlice = createSlice( {
  name: 'todo',
  initialState: { list: null, classList: null, loading: false, error: null } as TodoState,
  reducers: {
    invalidate: ( state ) => { state.list = null; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchFoundationClassList.fulfilled, ( state, action ) => { state.classList = action.payload; } )
      .addCase( fetchTodoList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchTodoList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload; } )
      .addCase( fetchTodoList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateTodo } = todoSlice.actions;
export default todoSlice.reducer;
