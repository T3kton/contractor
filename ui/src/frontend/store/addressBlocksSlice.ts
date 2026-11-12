import { Site_Site, Utilities_AddressBlock, Utilities_Address, Utilities_ReservedAddress, Utilities_DynamicAddress } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk, FETCH_ALL_COUNT } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface AddressBlockListItem {
  id: string;
  name: string;
  subnet: string;
  prefix: number;
  created: string;
  updated: string;
}

export interface AddressBlockDetail {
  addressBlock: Utilities_AddressBlock;
  addresses: Utilities_Address[];
  reserved: Utilities_ReservedAddress[];
  dynamic: Utilities_DynamicAddress[];
}


export const fetchAddressBlockList = createAuthThunk(
  'addressBlocks/fetchList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Utilities_AddressBlock._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Utilities_AddressBlock_list( { filter, position, count } ),
      contractor.Utilities_AddressBlock_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( ab: any ) => ( {
      id: ab.id.toString(),
      name: ab.name ?? '',
      subnet: ab.subnet ?? '',
      prefix: ab.prefix ?? 0,
      created: dateStr( ab.created ),
      updated: dateStr( ab.updated ),
    } ) ) as AddressBlockListItem[];
    return { items, total: listResult.total } as PagedResult<AddressBlockListItem>;
  }
);

export const fetchAddressBlock = createAuthThunk(
  'addressBlocks/fetchOne',
  async ( id: string, contractor ) =>
  {
    const abObj = new Utilities_AddressBlock( contractor, parseInt( id ) );
    const [ addressBlock, addresses, reserved, dynamic ] = await Promise.all( [
      contractor.Utilities_AddressBlock_get( parseInt( id ) ),
      contractor.Utilities_Address_get_multi( { filter: new Utilities_Address._ListFilter_address_block( abObj ), count: FETCH_ALL_COUNT } ),
      contractor.Utilities_ReservedAddress_get_multi( { filter: new Utilities_ReservedAddress._ListFilter_address_block( abObj ), count: FETCH_ALL_COUNT } ),
      contractor.Utilities_DynamicAddress_get_multi( { filter: new Utilities_DynamicAddress._ListFilter_address_block( abObj ), count: FETCH_ALL_COUNT } ),
    ] );
    return { addressBlock, addresses: Object.values( addresses ), reserved: Object.values( reserved ), dynamic: Object.values( dynamic ) } as AddressBlockDetail;
  }
);

const addressBlocksSlice = createPagedListSlice<AddressBlockListItem, AddressBlockDetail>( { name: 'addressBlocks', fetchList: fetchAddressBlockList, fetchOne: fetchAddressBlock } );

export const { invalidate: invalidateAddressBlocks } = addressBlocksSlice.actions;
export default addressBlocksSlice.reducer;
