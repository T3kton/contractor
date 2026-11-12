import { Directory_Zone, Directory_Entry } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk, FETCH_ALL_COUNT } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface DirectoryZoneListItem {
  id: string;
  name: string;
  fqdn: string;
  parent: string;
  created: string;
  updated: string;
}

export interface DirectoryZoneDetail {
  zone: Directory_Zone | null;
  parentName: string | null;
  entries: Directory_Entry[];
}

export const GLOBAL_ZONE_ID = 'global';

export const fetchDirectoryZoneList = createAuthThunk(
  'directory/fetchList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.Directory_Zone_list( { filter: undefined, position, count } ),
      contractor.Directory_Zone_get_multi( { filter: undefined, position, count } ),
    ] );
    const zones = Object.values( result );
    const nameById = new Map( zones.map( ( zone: any ) => [ zone.id.toString(), zone.name ?? '' ] ) );

    // parents outside this page aren't in nameById yet; resolve those separately
    const unknownParentIds = [ ...new Set(
      zones
        .map( ( zone: any ) => zone.parent?.toString() )
        .filter( ( parentId: string | undefined ): parentId is string => parentId !== undefined && !nameById.has( parentId ) )
    ) ];
    if ( unknownParentIds.length > 0 )
    {
      const parents = await Promise.all( unknownParentIds.map( ( parentId ) => contractor.Directory_Zone_get( parseInt( parentId ) ) ) );
      parents.forEach( ( parent ) => nameById.set( parent.id.toString(), parent.name ?? '' ) );
    }

    const items = zones.map( ( zone: any ) => ( {
      id: zone.id.toString(),
      name: zone.name ?? '',
      fqdn: zone.fqdn ?? '',
      parent: zone.parent !== undefined ? ( nameById.get( zone.parent.toString() ) ?? zone.parent.toString() ) : '',
      created: dateStr( zone.created ),
      updated: dateStr( zone.updated ),
    } ) ) as DirectoryZoneListItem[];
    return { items, total: listResult.total } as PagedResult<DirectoryZoneListItem>;
  }
);

export const fetchDirectoryZone = createAuthThunk(
  'directory/fetchOne',
  async ( id: string, contractor ) =>
  {
    if ( id === GLOBAL_ZONE_ID )
    {
      const allEntries = await contractor.Directory_Entry_get_multi( { filter: undefined, count: FETCH_ALL_COUNT } );
      const entries = Object.values( allEntries ).filter( ( entry ) => entry.zone === undefined );
      return { zone: null, parentName: null, entries } as DirectoryZoneDetail;
    }

    const zoneObj = new Directory_Zone( contractor, parseInt( id ) );
    const [ zone, entries ] = await Promise.all( [
      contractor.Directory_Zone_get( parseInt( id ) ),
      contractor.Directory_Entry_get_multi( { filter: new Directory_Entry._ListFilter_zone( zoneObj ), count: FETCH_ALL_COUNT } ),
    ] );
    const parentName = zone.parent !== undefined ? ( await contractor.Directory_Zone_get( zone.parent.id ) ).name ?? null : null;
    return { zone, parentName, entries: Object.values( entries ) } as DirectoryZoneDetail;
  }
);

const directorySlice = createPagedListSlice<DirectoryZoneListItem, DirectoryZoneDetail>( { name: 'directory', fetchList: fetchDirectoryZoneList, fetchOne: fetchDirectoryZone } );

export const { invalidate: invalidateDirectory } = directorySlice.actions;
export default directorySlice.reducer;
