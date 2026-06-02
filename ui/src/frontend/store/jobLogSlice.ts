import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import { Contractor, Site_Site, Foreman_JobLog } from '../lib/Contractor';
import { dateStr } from '../lib/utils';

export interface JobLogItem {
  id: string;
  job_id: string;
  site: string;
  target_class: string;
  target_description: string;
  script_name: string;
  creator: string;
  started_at: string;
  finished_at: string;
  canceled_by: string;
  canceled_at: string;
}

interface JobLogState {
  list: JobLogItem[] | null;
  loading: boolean;
  error: string | null;
}


export const fetchJobLogList = createAuthThunk(
  'jobLog/fetchList',
  async ( site: string, contractor ) =>
  {
    const filter = site ? new Foreman_JobLog._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const result = await contractor.Foreman_JobLog_get_multi( { filter } );
    return Object.values( result ).map( ( log: any ) => ( {
      id: log.id.toString(),
      job_id: String( log.job_id ?? '' ),
      site: log.site?.toString() ?? '',
      target_class: log.target_class ?? '',
      target_description: log.target_description ?? '',
      script_name: log.script_name ?? '',
      creator: log.creator ?? '',
      started_at: dateStr( log.started_at ),
      finished_at: dateStr( log.finished_at ),
      canceled_by: log.canceled_by ?? '',
      canceled_at: dateStr( log.canceled_at ),
    } ) ) as JobLogItem[];
  }
);

const jobLogSlice = createSlice( {
  name: 'jobLog',
  initialState: { list: null, loading: false, error: null } as JobLogState,
  reducers: {
    invalidate: ( state ) => { state.list = null; },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchJobLogList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchJobLogList.fulfilled, ( state, action ) => { state.loading = false; state.list = action.payload; } )
      .addCase( fetchJobLogList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateJobLog } = jobLogSlice.actions;
export default jobLogSlice.reducer;
