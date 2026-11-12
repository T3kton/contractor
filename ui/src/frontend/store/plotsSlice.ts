import type { Survey_Plot } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createPagedListSlice, createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';

export interface PlotListItem {
  name: string;
  created: string;
  updated: string;
}

export type PlotDetail = Survey_Plot;


export const fetchPlotList = createAuthThunk(
  'plots/fetchList',
  async ( { position, count }: PageParams, contractor ) =>
  {
    const [ listResult, result ] = await Promise.all( [
      contractor.Survey_Plot_list( { filter: undefined, position, count } ),
      contractor.Survey_Plot_get_multi( { filter: undefined, position, count } ),
    ] );
    const items = Object.values( result ).map( ( plot: any ) => ( {
      name: plot.name,
      created: dateStr( plot.created ),
      updated: dateStr( plot.updated ),
    } ) ) as PlotListItem[];
    return { items, total: listResult.total } as PagedResult<PlotListItem>;
  }
);

export const fetchPlot = createAuthThunk(
  'plots/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.Survey_Plot_get( id );
  }
);

const plotsSlice = createPagedListSlice<PlotListItem, PlotDetail>( { name: 'plots', fetchList: fetchPlotList, fetchOne: fetchPlot } );

export const { invalidate: invalidatePlots } = plotsSlice.actions;
export default plotsSlice.reducer;
