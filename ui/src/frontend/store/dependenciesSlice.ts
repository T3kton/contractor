import { Site_Site, Building_Dependency } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

export interface DependencyListItem {
  id: string;
  foundation: string;
  structure: string;
  script_name: string;
  state: string;
  created: string;
  updated: string;
}

export type DependencyDetail = Building_Dependency;


export const fetchDependencyList = createAuthThunk(
  'dependencies/fetchList',
  async ( site: string, contractor ) =>
  {
    const filter = site ? new Building_Dependency._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const result = await contractor.Building_Dependency_get_multi( { filter } );
    return Object.values( result ).map( ( dep: any ) => ( {
      id: dep.id.toString(),
      foundation: dep.foundation?.toString() ?? '',
      structure: dep.structure?.toString() ?? '',
      script_name: dep.create_script_name ?? '',
      state: dep.state ?? '',
      created: dateStr( dep.created ),
      updated: dateStr( dep.updated ),
    } ) ) as DependencyListItem[];
  }
);

export const fetchDependency = createAuthThunk(
  'dependencies/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.Building_Dependency_get( parseInt( id ) );
  }
);

const dependenciesSlice = createDetailListSlice<DependencyListItem, DependencyDetail>( { name: 'dependencies', fetchList: fetchDependencyList, fetchOne: fetchDependency } );

export const { invalidate: invalidateDependencies } = dependenciesSlice.actions;
export default dependenciesSlice.reducer;
