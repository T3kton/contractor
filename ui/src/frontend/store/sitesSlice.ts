import type { Site_Site } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

export interface SiteListItem {
  name: string;
  description: string;
  created: string;
  updated: string;
}

export type SiteDetail = Site_Site;



export const fetchSiteList = createAuthThunk(
  'sites/fetchList',
  async ( _: void, contractor ) =>
  {
    const result = await contractor.Site_Site_get_multi( { filter: undefined } );
    return Object.values( result ).map( ( site: any ) => ( {
      name: site.name,
      description: site.description,
      created: dateStr( site.created ),
      updated: dateStr( site.updated ),
    } ) ) as SiteListItem[];
  }
);

export const fetchSite = createAuthThunk(
  'sites/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.Site_Site_get( id );
  }
);

const sitesSlice = createDetailListSlice<SiteListItem, SiteDetail>( { name: 'sites', fetchList: fetchSiteList, fetchOne: fetchSite } );

export const { invalidate: invalidateSites } = sitesSlice.actions;
export default sitesSlice.reducer;
