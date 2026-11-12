import type { BluePrint_PXE } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface PXEListItem {
  name: string;
  created: string;
  updated: string;
}

export type PXEDetail = BluePrint_PXE;

export const fetchPXEList = createAuthThunk(
  'pxe/fetchList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.BluePrint_PXE_list( { filter: undefined, position, count } ),
      contractor.BluePrint_PXE_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( pxe: BluePrint_PXE ) => ( {
      name: pxe.name,
      created: dateStr( pxe.created ),
      updated: dateStr( pxe.updated ),
    } ) ) as PXEListItem[];
    return { items, total: listResult.total } as PagedResult<PXEListItem>;
  }
);

export const fetchPXE = createAuthThunk(
  'pxe/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.BluePrint_PXE_get( id )
  }
);

const pxeSlice = createPagedListSlice<PXEListItem, PXEDetail>( { name: 'pxe', fetchList: fetchPXEList, fetchOne: fetchPXE } );

export const { invalidate: invalidatePXE } = pxeSlice.actions;
export default pxeSlice.reducer;
