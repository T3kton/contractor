import type { BluePrint_PXE } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

export interface PXEListItem {
  name: string;
  created: string;
  updated: string;
}

export type PXEDetail = BluePrint_PXE;

export const fetchPXEList = createAuthThunk(
  'pxe/fetchList',
  async ( _: void, contractor ) =>
  {
    const result = await contractor.BluePrint_PXE_get_multi( { filter: undefined } );
    return Object.values( result ).map( ( pxe: BluePrint_PXE ) => ( {
      name: pxe.name,
      created: dateStr( pxe.created ),
      updated: dateStr( pxe.updated ),
    } ) ) as PXEListItem[];
  }
);

export const fetchPXE = createAuthThunk(
  'pxe/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.BluePrint_PXE_get( id )
  }
);

const pxeSlice = createDetailListSlice<PXEListItem, PXEDetail>( { name: 'pxe', fetchList: fetchPXEList, fetchOne: fetchPXE } );

export const { invalidate: invalidatePXE } = pxeSlice.actions;
export default pxeSlice.reducer;
