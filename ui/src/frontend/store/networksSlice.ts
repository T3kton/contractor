import { Site_Site, Utilities_Network, Utilities_NetworkAddressBlock } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

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
  async ( site: string, contractor ) =>
  {
    const filter = site ? new Utilities_Network._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const result = await contractor.Utilities_Network_get_multi( { filter } );
    return Object.values( result ).map( ( network: any ) => ( {
      id: network.id.toString(),
      name: network.name,
      created: dateStr( network.created ),
      updated: dateStr( network.updated ),
    } ) ) as NetworkListItem[];
  }
);

export const fetchNetwork = createAuthThunk(
  'networks/fetchOne',
  async ( id: string, contractor ) =>
  {
    const network = await contractor.Utilities_Network_get( parseInt( id ) );
    const nabResult = await contractor.Utilities_NetworkAddressBlock_get_multi( {
      filter: new Utilities_NetworkAddressBlock._ListFilter_network( new Utilities_Network( contractor, parseInt( id ) ) ),
    } );
    return { network, networkAddressBlocks: Object.values( nabResult ) } as NetworkDetail;
  }
);

const networksSlice = createDetailListSlice<NetworkListItem, NetworkDetail>( { name: 'networks', fetchList: fetchNetworkList, fetchOne: fetchNetwork } );

export const { invalidate: invalidateNetworks } = networksSlice.actions;
export default networksSlice.reducer;
