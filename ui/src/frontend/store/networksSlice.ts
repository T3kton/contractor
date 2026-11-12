import { Site_Site, Utilities_Network, Utilities_NetworkAddressBlock } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk, FETCH_ALL_COUNT } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface NetworkListItem {
  id: string;
  name: string;
  created: string;
  updated: string;
}

export interface NetworkDetail {
  network: Utilities_Network;
  networkAddressBlocks: Utilities_NetworkAddressBlock[];
}

export const fetchNetworkList = createAuthThunk(
  'networks/fetchList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Utilities_Network._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Utilities_Network_list( { filter, position, count } ),
      contractor.Utilities_Network_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( network: any ) => ( {
      id: network.id.toString(),
      name: network.name,
      created: dateStr( network.created ),
      updated: dateStr( network.updated ),
    } ) ) as NetworkListItem[];
    return { items, total: listResult.total } as PagedResult<NetworkListItem>;
  }
);

export const fetchNetwork = createAuthThunk(
  'networks/fetchOne',
  async ( id: string, contractor ) =>
  {
    const network = await contractor.Utilities_Network_get( parseInt( id ) );
    const nabResult = await contractor.Utilities_NetworkAddressBlock_get_multi( {
      filter: new Utilities_NetworkAddressBlock._ListFilter_network( new Utilities_Network( contractor, parseInt( id ) ) ),
      count: FETCH_ALL_COUNT,
    } );
    return { network, networkAddressBlocks: Object.values( nabResult ) } as NetworkDetail;
  }
);

const networksSlice = createPagedListSlice<NetworkListItem, NetworkDetail>( { name: 'networks', fetchList: fetchNetworkList, fetchOne: fetchNetwork } );

export const { invalidate: invalidateNetworks } = networksSlice.actions;
export default networksSlice.reducer;
