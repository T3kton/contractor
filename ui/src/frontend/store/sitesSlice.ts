import type { Site_Site } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface SiteListItem {
  name: string;
  description: string;
  created: string;
  updated: string;
}

export type SiteDetail = Site_Site;



export const fetchSiteList = createAuthThunk(
  'sites/fetchList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.Site_Site_list( { filter: undefined, position, count } ),
      contractor.Site_Site_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( site: any ) => ( {
      name: site.name,
      description: site.description,
      created: dateStr( site.created ),
      updated: dateStr( site.updated ),
    } ) ) as SiteListItem[];
    return { items, total: listResult.total } as PagedResult<SiteListItem>;
  }
);

export const fetchSite = createAuthThunk(
  'sites/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.Site_Site_get( id );
  }
);

const sitesSlice = createPagedListSlice<SiteListItem, SiteDetail>( { name: 'sites', fetchList: fetchSiteList, fetchOne: fetchSite } );

export const { invalidate: invalidateSites } = sitesSlice.actions;
export default sitesSlice.reducer;
