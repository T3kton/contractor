import type { BluePrint_FoundationBluePrint, BluePrint_StructureBluePrint } from '../lib/Contractor';
import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';
import { dateStr } from '../lib/utils';

export interface BluePrintListItem {
  name: string;
  description: string;
  created: string;
  updated: string;
}

export type BluePrintDetail = BluePrint_FoundationBluePrint | BluePrint_StructureBluePrint;

interface BluePrintsState {
  listF: BluePrintListItem[] | null;
  totalF: number;
  listS: BluePrintListItem[] | null;
  totalS: number;
  detail: BluePrintDetail | null;
  loading: boolean;
  error: string | null;
}


export const fetchFoundationBluePrintList = createAuthThunk(
  'blueprints/fetchFoundationList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.BluePrint_FoundationBluePrint_list( { filter: undefined, position, count } ),
      contractor.BluePrint_FoundationBluePrint_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( bp: any ) => ( {
      name: bp.name,
      description: bp.description,
      created: dateStr( bp.created ),
      updated: dateStr( bp.updated ),
    } ) ) as BluePrintListItem[];
    return { items, total: listResult.total } as PagedResult<BluePrintListItem>;
  }
);

export const fetchStructureBluePrintList = createAuthThunk(
  'blueprints/fetchStructureList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.BluePrint_StructureBluePrint_list( { filter: undefined, position, count } ),
      contractor.BluePrint_StructureBluePrint_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( bp: any ) => ( {
      name: bp.name,
      description: bp.description,
      created: dateStr( bp.created ),
      updated: dateStr( bp.updated ),
    } ) ) as BluePrintListItem[];
    return { items, total: listResult.total } as PagedResult<BluePrintListItem>;
  }
);

export const fetchFoundationBluePrint = createAuthThunk(
  'blueprints/fetchFoundation',
  async ( id: string, contractor ) =>
  {
    return await contractor.BluePrint_FoundationBluePrint_get( id );
  }
);

export const fetchStructureBluePrint = createAuthThunk(
  'blueprints/fetchStructure',
  async ( id: string, contractor ) =>
  {
    return await contractor.BluePrint_StructureBluePrint_get( id );
  }
);

const blueprintsSlice = createSlice( {
  name: 'blueprints',
  initialState: { listF: null, totalF: 0, listS: null, totalS: 0, detail: null, loading: false, error: null } as BluePrintsState,
  reducers: {
    invalidate: ( state ) => { state.listF = null; state.totalF = 0; state.listS = null; state.totalS = 0; state.detail = null; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchFoundationBluePrintList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchFoundationBluePrintList.fulfilled, ( state, action ) => { state.loading = false; state.listF = action.payload.items; state.totalF = action.payload.total; } )
      .addCase( fetchFoundationBluePrintList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchStructureBluePrintList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchStructureBluePrintList.fulfilled, ( state, action ) => { state.loading = false; state.listS = action.payload.items; state.totalS = action.payload.total; } )
      .addCase( fetchStructureBluePrintList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchFoundationBluePrint.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchFoundationBluePrint.fulfilled, ( state, action ) => { state.loading = false; state.detail = action.payload as any; } )
      .addCase( fetchFoundationBluePrint.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchStructureBluePrint.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchStructureBluePrint.fulfilled, ( state, action ) => { state.loading = false; state.detail = action.payload as any; } )
      .addCase( fetchStructureBluePrint.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateBlueprints } = blueprintsSlice.actions;
export default blueprintsSlice.reducer;
