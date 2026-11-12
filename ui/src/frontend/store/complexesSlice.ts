import { Site_Site, Building_Complex } from '../lib/Contractor';
import type Contractor from '../lib/Contractor';
import { dateStr, extraAttributes } from '../lib/utils';
import type { ModelAttribute } from '../lib/utils';
import { createPagedListSlice, createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

// the complex subclass to fetch for a given Complex.type, the generated accessors are named
// '{Namespace}_{Model}_get'.  Types with no entry simply get no extra attributes.
// NOTE: Manual_ManualComplex/Test_TestComplex are the *Complexes*; the similarly named
// Manual_ManualComplexedFoundation/Test_TestComplexedFoundation are Foundations (see
// foundationsSlice) -- easy to mix up.
const COMPLEX_GET: Record<string, ( c: Contractor, id: string ) => Promise<any>> = {
  'Azure': ( c, id ) => c.Azure_AzureComplex_get( id ),
  'Docker': ( c, id ) => c.Docker_DockerComplex_get( id ),
  'LibVirt': ( c, id ) => c.LibVirt_LibVirtComplex_get( id ),
  'Manual': ( c, id ) => c.Manual_ManualComplex_get( id ),
  'Proxmox': ( c, id ) => c.Proxmox_ProxmoxComplex_get( id ),
  'Test': ( c, id ) => c.Test_TestComplex_get( id ),
  'VCenter': ( c, id ) => c.VCenter_VCenterComplex_get( id ),
  'VirtualBox': ( c, id ) => c.VirtualBox_VirtualBoxComplex_get( id ),
};

const typeAttributes = async ( contractor: Contractor, id: string, type: string | undefined ): Promise<ModelAttribute[]> =>
{
  const getter = type !== undefined ? COMPLEX_GET[ type ] : undefined;
  if ( getter === undefined ) return [];

  try
  {
    // the base instance is what tells us which attributes are the type specific ones
    return extraAttributes( await getter( contractor, id ), new Building_Complex( contractor ) );
  }
  catch ( err )  // don't lose the rest of the detail page over the extra attributes
  {
    return [];
  }
};

export interface ComplexListItem {
  id: string;
  description: string;
  type: string;
  state: string;
  created: string;
  updated: string;
}

export interface ComplexDetail {
  complex: Building_Complex;
  attributes: ModelAttribute[];
}


export const fetchComplexList = createAuthThunk(
  'complexes/fetchList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Building_Complex._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Building_Complex_list( { filter, position, count } ),
      contractor.Building_Complex_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( c: any ) => ( {
      id: c.name,
      description: c.description ?? '',
      type: c.type ?? '',
      state: c.state ?? '',
      created: dateStr( c.created ),
      updated: dateStr( c.updated ),
    } ) ) as ComplexListItem[];
    return { items, total: listResult.total } as PagedResult<ComplexListItem>;
  }
);

export const fetchComplex = createAuthThunk(
  'complexes/fetchOne',
  async ( id: string, contractor ) =>
  {
    const complex = await contractor.Building_Complex_get( id );
    const attributes = await typeAttributes( contractor, id, complex.type );
    return { complex, attributes } as ComplexDetail;
  }
);

const complexesSlice = createPagedListSlice<ComplexListItem, ComplexDetail>( { name: 'complexes', fetchList: fetchComplexList, fetchOne: fetchComplex } );

export const { invalidate: invalidateComplexes } = complexesSlice.actions;
export default complexesSlice.reducer;
