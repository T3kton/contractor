import { Site_Site, Building_Structure, Utilities_Address } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk, FETCH_ALL_COUNT } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface StructureListItem {
  id: string;
  hostname: string;
  state: string;
  created: string;
  updated: string;
}

export interface StructureDetail {
  structure: Building_Structure;
  addresses: Utilities_Address[];
}


export const fetchStructureList = createAuthThunk(
  'structures/fetchList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Building_Structure._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Building_Structure_list( { filter, position, count } ),
      contractor.Building_Structure_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( s: any ) => ( {
      id: s.id.toString(),
      hostname: s.hostname ?? '',
      state: s.state ?? '',
      created: dateStr( s.created ),
      updated: dateStr( s.updated ),
    } ) ) as StructureListItem[];
    return { items, total: listResult.total } as PagedResult<StructureListItem>;
  }
);

export const fetchStructure = createAuthThunk(
  'structures/fetchOne',
  async ( id: string, contractor ) =>
  {
    const structure = await contractor.Building_Structure_get( parseInt( id ) );
    const addrResult = await contractor.Utilities_Address_get_multi( {
      filter: new Utilities_Address._ListFilter_structure( new Building_Structure( contractor, parseInt( id ) ) ),
      count: FETCH_ALL_COUNT,
    } );
    return { structure, addresses: Object.values( addrResult ) } as StructureDetail;
  }
);

const structuresSlice = createPagedListSlice<StructureListItem, StructureDetail>( { name: 'structures', fetchList: fetchStructureList, fetchOne: fetchStructure } );

export const { invalidate: invalidateStructures } = structuresSlice.actions;
export default structuresSlice.reducer;
