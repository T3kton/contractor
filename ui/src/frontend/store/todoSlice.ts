import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';
import { Site_Site, Building_Foundation } from '../lib/Contractor';
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
  total: number;
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
  async ( { site, hasDependancies, foundationClass, position, count }: { site: string; hasDependancies: boolean; foundationClass: string | null } & PageParams, contractor ) =>
  {
    const filter = site
      ? new Building_Foundation._ListFilter_todo( new Site_Site( contractor, site ), hasDependancies, foundationClass || '' )
      : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Building_Foundation_list( { filter, position, count } ),
      contractor.Building_Foundation_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( f: any ) => ( {
      id: f.locator,
      locator: f.locator,
      dependencyCount: ' ',
      complex: ' ',
      created: dateStr( f.created ),
      updated: dateStr( f.updated ),
    } ) ) as TodoFoundationItem[];
    return { items, total: listResult.total } as PagedResult<TodoFoundationItem>;
  }
);

const todoSlice = createSlice( {
  name: 'todo',
  initialState: { list: null, total: 0, classList: null, loading: false, error: null } as TodoState,
  reducers: {
    invalidate: ( state ) => { state.list = null; state.total = 0; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchFoundationClassList.fulfilled, ( state, action ) => { state.classList = action.payload; } )
      .addCase( fetchTodoList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchTodoList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload.items; state.total = action.payload.total; } )
      .addCase( fetchTodoList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateTodo } = todoSlice.actions;
export default todoSlice.reducer;
