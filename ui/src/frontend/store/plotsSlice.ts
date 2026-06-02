import type { Survey_Plot } from '../lib/Contractor';
import { dateStr } from '../lib/utils';
import { createDetailListSlice, createAuthThunk } from './sliceFactory';

export interface PlotListItem {
  name: string;
  created: string;
  updated: string;
}

export type PlotDetail = Survey_Plot;


export const fetchPlotList = createAuthThunk(
  'plots/fetchList',
  async ( _: void, contractor ) =>
  {
    const result = await contractor.Survey_Plot_get_multi( { filter: undefined } );
    return Object.values( result ).map( ( plot: any ) => ( {
      name: plot.name,
      created: dateStr( plot.created ),
      updated: dateStr( plot.updated ),
    } ) ) as PlotListItem[];
  }
);

export const fetchPlot = createAuthThunk(
  'plots/fetchOne',
  async ( id: string, contractor ) =>
  {
    return await contractor.Survey_Plot_get( id );
  }
);

const plotsSlice = createDetailListSlice<PlotListItem, PlotDetail>( { name: 'plots', fetchList: fetchPlotList, fetchOne: fetchPlot } );

export const { invalidate: invalidatePlots } = plotsSlice.actions;
export default plotsSlice.reducer;
