import { Site_Site, Building_Foundation, Building_Dependency } from '../lib/Contractor';
import type Contractor from '../lib/Contractor';
import { dateStr, extraAttributes } from '../lib/utils';
import type { ModelAttribute } from '../lib/utils';
import { createPagedListSlice, createAuthThunk, FETCH_ALL_COUNT } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

// the foundation subclass to fetch for a given Foundation.type, the generated accessors are
// named '{Namespace}_{Model}_get'.  Types with no entry (ie: a plugin whose client has not been
// regenerated) simply get no extra attributes rather than an error.
const FOUNDATION_GET: Record<string, ( c: Contractor, id: string ) => Promise<any>> = {
  'AMT': ( c, id ) => c.AMT_AMTFoundation_get( id ),
  'Azure': ( c, id ) => c.Azure_AzureFoundation_get( id ),
  'Docker': ( c, id ) => c.Docker_DockerFoundation_get( id ),
  'IPMI': ( c, id ) => c.IPMI_IPMIFoundation_get( id ),
  'LibVirt': ( c, id ) => c.LibVirt_LibVirtFoundation_get( id ),
  'Manual': ( c, id ) => c.Manual_ManualFoundation_get( id ),
  'ManualComplex': ( c, id ) => c.Manual_ManualComplexedFoundation_get( id ),
  'Proxmox': ( c, id ) => c.Proxmox_ProxmoxFoundation_get( id ),
  'RedFish': ( c, id ) => c.RedFish_RedFishFoundation_get( id ),
  'Test': ( c, id ) => c.Test_TestFoundation_get( id ),
  'TestComplex': ( c, id ) => c.Test_TestComplexedFoundation_get( id ),
  'VCenter': ( c, id ) => c.VCenter_VCenterFoundation_get( id ),
  'VirtualBox': ( c, id ) => c.VirtualBox_VirtualBoxFoundation_get( id ),
};

const typeAttributes = async ( contractor: Contractor, id: string, type: string | undefined ): Promise<ModelAttribute[]> =>
{
  const getter = type !== undefined ? FOUNDATION_GET[ type ] : undefined;
  if ( getter === undefined ) return [];

  try
  {
    // the base instance is what tells us which attributes are the type specific ones
    return extraAttributes( await getter( contractor, id ), new Building_Foundation( contractor ) );
  }
  catch ( err )  // don't lose the rest of the detail page over the extra attributes
  {
    return [];
  }
};

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
  attributes: ModelAttribute[];
}


export const fetchFoundationList = createAuthThunk(
  'foundations/fetchList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Building_Foundation._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Building_Foundation_list( { filter, position, count } ),
      contractor.Building_Foundation_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( f: any ) => ( {
      id: f.locator,
      locator: f.locator,
      site: f.site?.toString() ?? '',
      type: f.type ?? '',
      state: f.state ?? '',
      created: dateStr( f.created ),
      updated: dateStr( f.updated ),
    } ) ) as FoundationListItem[];
    return { items, total: listResult.total } as PagedResult<FoundationListItem>;
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
      count: FETCH_ALL_COUNT,
    } );
    const attributes = await typeAttributes( contractor, id, foundation.type );
    return { foundation, interface_list, dependencies: Object.values( depResult ), attributes } as FoundationDetail;
  }
);

const foundationsSlice = createPagedListSlice<FoundationListItem, FoundationDetail>( { name: 'foundations', fetchList: fetchFoundationList, fetchOne: fetchFoundation } );

export const { invalidate: invalidateFoundations } = foundationsSlice.actions;
export default foundationsSlice.reducer;
