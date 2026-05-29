import { Site_Site, Building_Foundation, Building_Dependency } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

export interface FoundationListItem {
  id: string;
  locator: string;
  site: string;
  type: string;
  state: string;
  created: string;
  updated: string;
}

export interface FoundationDetail {
  foundation: Building_Foundation;
  interface_list: any[];
  dependencies: Building_Dependency[];
}


export const fetchFoundationList = createAuthThunk(
  'foundations/fetchList',
  async ( site: string, contractor ) =>
  {
    const filter = site ? new Building_Foundation._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const result = await contractor.Building_Foundation_get_multi( { filter } );
    return Object.values( result ).map( ( f: any ) => ( {
      id: f.locator,
      locator: f.locator,
      site: f.site?.toString() ?? '',
      type: f.type ?? '',
      state: f.state ?? '',
      created: dateStr( f.created ),
      updated: dateStr( f.updated ),
    } ) ) as FoundationListItem[];
  }
);

export const fetchFoundation = createAuthThunk(
  'foundations/fetchOne',
  async ( id: string, contractor ) =>
  {
    const foundation = await contractor.Building_Foundation_get( id );
    const interface_list = await contractor.Building_Foundation_call_getInterfaceList( id );
    const depResult = await contractor.Building_Dependency_get_multi( {
      filter: new Building_Dependency._ListFilter_foundation( new Building_Foundation( contractor, id ) ),
    } );
    return { foundation, interface_list, dependencies: Object.values( depResult ) } as FoundationDetail;
  }
);

const foundationsSlice = createDetailListSlice<FoundationListItem, FoundationDetail>( { name: 'foundations', fetchList: fetchFoundationList, fetchOne: fetchFoundation } );

export const { invalidate: invalidateFoundations } = foundationsSlice.actions;
export default foundationsSlice.reducer;
