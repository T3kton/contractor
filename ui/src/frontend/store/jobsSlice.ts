import { createSlice } from '@reduxjs/toolkit';
import { createAuthThunk } from './sliceFactory';
import type { PageParams, PagedResult } from './sliceFactory';
import { Site_Site, Foreman_FoundationJob, Foreman_StructureJob, Foreman_DependencyJob } from '../lib/Contractor';
import { dateStr } from '../lib/utils';

export interface JobListItem {
  id: string;
  script: string;
  foundation?: string;
  structure?: string;
  dependency?: string;
  message: string;
  note: string;
  status: any[];
  state: string;
  created: string;
  updated: string;
}

export interface JobDetail {
  job: Foreman_FoundationJob | Foreman_StructureJob | Foreman_DependencyJob;
  jobURI: string;
  canPause: boolean;
  canResume: boolean;
  canReset: boolean;
  canRollback: boolean;
}

interface JobsState {
  listFoundation: JobListItem[] | null;
  totalFoundation: number;
  listStructure: JobListItem[] | null;
  totalStructure: number;
  listDependency: JobListItem[] | null;
  totalDependency: number;
  detail: JobDetail | null;
  loading: boolean;
  error: string | null;
}


const parseJobStatus = ( statusStr: string | undefined ): any[] =>
{
  try {
    return JSON.parse( ( statusStr || '[]' ).replaceAll( "'", '"' ).replaceAll( 'False', 'false' ).replaceAll( 'True', 'true' ).replaceAll( 'None', 'null' ) );
  } catch {
    return [];
  }
};

export const fetchFoundationJobList = createAuthThunk(
  'jobs/fetchFoundationList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Foreman_FoundationJob._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Foreman_FoundationJob_list( { filter, position, count } ),
      contractor.Foreman_FoundationJob_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( job: any ) => ( {
      id: job.id.toString(),
      script: job.script_name ?? '',
      foundation: job.foundation?.toString(),
      message: job.message ?? '',
      note: job.note ?? '',
      status: parseJobStatus( job.status ),
      state: job.state ?? '',
      created: dateStr( job.created ),
      updated: dateStr( job.updated ),
    } ) ) as JobListItem[];
    return { items, total: listResult.total } as PagedResult<JobListItem>;
  }
);

export const fetchStructureJobList = createAuthThunk(
  'jobs/fetchStructureList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Foreman_StructureJob._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Foreman_StructureJob_list( { filter, position, count } ),
      contractor.Foreman_StructureJob_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( job: any ) => ( {
      id: job.id.toString(),
      script: job.script_name ?? '',
      structure: job.structure?.toString(),
      message: job.message ?? '',
      note: job.note ?? '',
      status: parseJobStatus( job.status ),
      state: job.state ?? '',
      created: dateStr( job.created ),
      updated: dateStr( job.updated ),
    } ) ) as JobListItem[];
    return { items, total: listResult.total } as PagedResult<JobListItem>;
  }
);

export const fetchDependencyJobList = createAuthThunk(
  'jobs/fetchDependencyList',
  async ( { site, position, count }: { site: string } & PageParams, contractor ) =>
  {
    const filter = site ? new Foreman_DependencyJob._ListFilter_site( new Site_Site( contractor, site ) ) : undefined;
    const [ listResult, result ] = await Promise.all( [
      contractor.Foreman_DependencyJob_list( { filter, position, count } ),
      contractor.Foreman_DependencyJob_get_multi( { filter, position, count } ),
    ] );
    const items = Object.values( result ).map( ( job: any ) => ( {
      id: job.id.toString(),
      script: job.script_name ?? '',
      dependency: job.dependency?.toString(),
      message: job.message ?? '',
      note: job.note ?? '',
      status: parseJobStatus( job.status ),
      state: job.state ?? '',
      created: dateStr( job.created ),
      updated: dateStr( job.updated ),
    } ) ) as JobListItem[];
    return { items, total: listResult.total } as PagedResult<JobListItem>;
  }
);

export const fetchJobDetail = createAuthThunk(
  'jobs/fetchDetail',
  async ( { id, jobType }: { id: string; jobType: string }, contractor ) =>
  {
    const numId = parseInt( id );
    let job: Foreman_FoundationJob | Foreman_StructureJob | Foreman_DependencyJob;
    if ( jobType === 'foundation' )
      job = await contractor.Foreman_FoundationJob_get( numId );
    else if ( jobType === 'structure' )
      job = await contractor.Foreman_StructureJob_get( numId );
    else if ( jobType === 'dependency' )
      job = await contractor.Foreman_DependencyJob_get( numId );
    else
      throw new Error( 'Unknown job type: ' + jobType );

    let canPause = false, canResume = false, canReset = false, canRollback = false;
    if ( job.state === 'paused' ) canResume = true;
    else if ( job.state === 'queued' ) canPause = true;
    else if ( job.state === 'error' ) { canReset = true; canRollback = true; }

    return { job, jobURI: job.toURL(), canPause, canResume, canReset, canRollback } as JobDetail;
  }
);

export const pauseJob = createAuthThunk(
  'jobs/pause',
  async ( uri: string, contractor ) =>
  {
    const id = parseInt( uri.split( ':' )[ 1 ] );
    await contractor.Foreman_BaseJob_call_pause( id );
  }
);

export const resumeJob = createAuthThunk(
  'jobs/resume',
  async ( uri: string, contractor ) =>
  {
    const id = parseInt( uri.split( ':' )[ 1 ] );
    await contractor.Foreman_BaseJob_call_resume( id );
  }
);

export const resetJob = createAuthThunk(
  'jobs/reset',
  async ( uri: string, contractor ) =>
  {
    const id = parseInt( uri.split( ':' )[ 1 ] );
    await contractor.Foreman_BaseJob_call_reset( id );
  }
);

export const rollbackJob = createAuthThunk(
  'jobs/rollback',
  async ( uri: string, contractor ) =>
  {
    const id = parseInt( uri.split( ':' )[ 1 ] );
    await contractor.Foreman_BaseJob_call_rollback( id );
  }
);

const jobsSlice = createSlice( {
  name: 'jobs',
  initialState: {
    listFoundation: null,
    totalFoundation: 0,
    listStructure: null,
    totalStructure: 0,
    listDependency: null,
    totalDependency: 0,
    detail: null,
    loading: false,
    error: null,
  } as JobsState,
  reducers: {
    invalidate: ( state ) => {
      state.listFoundation = null;
      state.totalFoundation = 0;
      state.listStructure = null;
      state.totalStructure = 0;
      state.listDependency = null;
      state.totalDependency = 0;
      state.detail = null;
    },
  },
  extraReducers: ( builder ) =>
  {
    builder
      .addCase( fetchFoundationJobList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchFoundationJobList.fulfilled, ( state, action ) => { state.loading = false; state.listFoundation = action.payload.items; state.totalFoundation = action.payload.total; } )
      .addCase( fetchFoundationJobList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchStructureJobList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchStructureJobList.fulfilled, ( state, action ) => { state.loading = false; state.listStructure = action.payload.items; state.totalStructure = action.payload.total; } )
      .addCase( fetchStructureJobList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchDependencyJobList.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchDependencyJobList.fulfilled, ( state, action ) => { state.loading = false; state.listDependency = action.payload.items; state.totalDependency = action.payload.total; } )
      .addCase( fetchDependencyJobList.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } )
      .addCase( fetchJobDetail.pending, ( state ) => { state.loading = true; state.error = null; } )
      .addCase( fetchJobDetail.fulfilled, ( state, action ) => { state.loading = false; state.detail = action.payload; } )
      .addCase( fetchJobDetail.rejected, ( state, action ) => { state.loading = false; state.error = ( ( action.payload as any )?.msg ) ?? action.error.message ?? 'Error loading data'; } );
  },
} );

export const { invalidate: invalidateJobs } = jobsSlice.actions;
export default jobsSlice.reducer;
