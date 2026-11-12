import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationJobList, fetchStructureJobList, fetchDependencyJobList, fetchJobDetail, pauseJob, resumeJob, resetJob, rollbackJob } from '../store/jobsSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import JobStateDialog from './JobStateDialog';
import { Box, Button, Chip, CircularProgress, Link, Snackbar, Alert, Table, TableBody, TableCell, TableHead, TablePagination, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr, stateColor } from '../lib/utils';

interface Props {
  id?: string;
  jobType?: string;
  site?: string;
}

const renderStatus = ( item: any, idx: number ) =>
{
  const percent = item.percent.toLocaleString( undefined, { minimumFractionDigits: 2 } );

  if ( item.operation === 'Function' && item.parameters?.dispatched )
    return <Box key={ idx }><strong>Task Dispatched</strong></Box>;

  if ( item.operation === 'Scope' )
  {
    if ( item.parameters === null )
      return <Box key={ idx }>{ percent }%</Box>;

    if ( item.parameters?.time_remaining )
    {
      if ( item.parameters.time_remaining[0] === '-' )
        return <Box key={ idx } sx={{ bgcolor: 'orange' }}><strong>{ item.parameters.description }</strong> { percent }% Elapsed:&nbsp;{ item.parameters.time_elapsed } Remaining:&nbsp;{ item.parameters.time_remaining }</Box>;

      return <Box key={ idx }><strong>{ item.parameters.description }</strong> { percent }% Elapsed:&nbsp;{ item.parameters.time_elapsed } Remaining:&nbsp;{ item.parameters.time_remaining }</Box>;
    }

    return <Box key={ idx }><strong>{ item.parameters.description }</strong> { percent }% Elapsed:&nbsp;{ item.parameters.time_elapsed }</Box>;
  }

  return null;
};

const Job: React.FC<Props> = ( { id, jobType, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { listFoundation, totalFoundation, listStructure, totalStructure, listDependency, totalDependency, detail, loading, error } = useSelector( ( s: RootState ) => s.jobs );
  const [snackMessage, setSnackMessage] = useState( '' );
  const [snackSeverity, setSnackSeverity] = useState<'success' | 'error'>( 'success' );
  const [snackOpen, setSnackOpen] = useState( false );
  const [pageF, setPageF] = useState( 0 );
  const [pageS, setPageS] = useState( 0 );
  const [pageD, setPageD] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );
  const actionGenRef = useRef( 0 );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchJobDetail( { id, jobType: jobType ?? '' } ) );
    else
    {
      dispatch( fetchFoundationJobList( { site: site ?? '', position: pageF * rowsPerPage, count: rowsPerPage } ) );
      dispatch( fetchStructureJobList( { site: site ?? '', position: pageS * rowsPerPage, count: rowsPerPage } ) );
      dispatch( fetchDependencyJobList( { site: site ?? '', position: pageD * rowsPerPage, count: rowsPerPage } ) );
    }
  }, [authenticated, dispatch, id, jobType, site, pageF, pageS, pageD, rowsPerPage, updateVersion] );

  useEffect( () => { setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); }, [site] );
  useEffect( () => { fetchData(); }, [fetchData] );

  const showSnack = ( message: string, severity: 'success' | 'error' ) =>
  {
    setSnackMessage( message );
    setSnackSeverity( severity );
    setSnackOpen( true );
  };

  const makeActionHandler = ( action: any, label: string ) => () =>
  {
    const gen = ++actionGenRef.current;
    dispatch( action( detail!.jobURI ) )
      .unwrap()
      .then( () =>
      {
        if ( gen === actionGenRef.current )
        {
          dispatch( fetchJobDetail( { id: id!, jobType: jobType! } ) );
          showSnack( label, 'success' );
        }
      } )
      .catch( ( err: any ) => showSnack( 'Error: "' + ( err?.msg ?? String( err ) ) + '"', 'error' ) );
  };

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  const snackbar = (
    <Snackbar open={ snackOpen } autoHideDuration={ 4000 } onClose={ () => setSnackOpen( false ) }>
      <Alert severity={ snackSeverity } onClose={ () => setSnackOpen( false ) }>{ snackMessage }</Alert>
    </Snackbar>
  );

  if ( id !== undefined )
  {
    const j = detail?.job as any;
    return (
      <Box>
        <Link component={ RouterLink } to="/jobs">&larr; Jobs</Link>
        <Typography variant="h5" gutterBottom>Job Detail</Typography>
        { detail !== null &&
          <Box>
            <Box sx={{ mb: 1 }}>
              <Button onClick={ makeActionHandler( pauseJob, 'Job Paused' ) } disabled={ !detail.canPause }>Pause</Button>
              <Button onClick={ makeActionHandler( resumeJob, 'Job Resumed' ) } disabled={ !detail.canResume }>Resume</Button>
              <Button onClick={ makeActionHandler( resetJob, 'Job Reset' ) } disabled={ !detail.canReset }>Reset</Button>
              <Button onClick={ makeActionHandler( rollbackJob, 'Job Rolled Back' ) } disabled={ !detail.canRollback }>Rollback</Button>
              <JobStateDialog getState={ ( uri: string ) => { const jid = parseInt( uri.split( ':' )[ 1 ] ); return Promise.all( [ contractor.Foreman_BaseJob_call_jobRunnerVariables( jid ), contractor.Foreman_BaseJob_call_jobRunnerState( jid ) ] ); } } uri={ detail.jobURI } />
            </Box>
            <Table size="small" sx={{ mt: 1 }}>
              <TableBody>
                <TableRow><TableCell variant="head">Site</TableCell><TableCell><Link component={ RouterLink } to={ '/site/' + j?.site?.toString() }>{ j?.site?.toString() }</Link></TableCell></TableRow>
                { j?.foundation !== undefined &&
                  <TableRow><TableCell variant="head">Foundation</TableCell><TableCell><Link component={ RouterLink } to={ '/foundation/' + j.foundation?.toString() }>{ j.foundation?.toString() }</Link></TableCell></TableRow>
                }
                { j?.structure !== undefined &&
                  <TableRow><TableCell variant="head">Structure</TableCell><TableCell><Link component={ RouterLink } to={ '/structure/' + j.structure?.toString() }>{ j.structure?.toString() }</Link></TableCell></TableRow>
                }
                <TableRow><TableCell variant="head">Script</TableCell><TableCell>{ detail.job.script_name }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Message</TableCell><TableCell>{ detail.job.message }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Note</TableCell><TableCell>{ detail.job.note }</TableCell></TableRow>
                <TableRow><TableCell variant="head">State</TableCell><TableCell><Chip size="small" label={ detail.job.state } color={ stateColor( detail.job.state ?? '' ) } /></TableCell></TableRow>
                <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.job.created ) }</TableCell></TableRow>
                <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.job.updated ) }</TableCell></TableRow>
              </TableBody>
            </Table>
          </Box>
        }
        { snackbar }
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Foundation Jobs</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Script</TableCell>
            <TableCell>Foundation</TableCell>
            <TableCell>Message</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Dates</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( listFoundation || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/f/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/foundation/' + item.foundation }>{ item.foundation }</Link></TableCell>
              <TableCell>{ item.message }{ item.note && <><br/>{ item.note }</> }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ totalFoundation } page={ pageF } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [25, 50, 100] } onPageChange={ ( _, p ) => setPageF( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

      <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>Structure Jobs</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Script</TableCell>
            <TableCell>Structure</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Dates</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( listStructure || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/s/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/structure/' + item.structure }>{ item.structure }</Link></TableCell>
              <TableCell>{ item.message }{ item.note && <><br/>{ item.note }</> }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ totalStructure } page={ pageS } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [25, 50, 100] } onPageChange={ ( _, p ) => setPageS( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

      <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>Dependency Jobs</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell align="right">Id</TableCell>
            <TableCell>Script</TableCell>
            <TableCell>Dependency</TableCell>
            <TableCell>Message</TableCell>
            <TableCell>State</TableCell>
            <TableCell>Dates</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( listDependency || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/d/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell>{ item.dependency }</TableCell>
              <TableCell>{ item.message }{ item.note && <><br/>{ item.note }</> }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ totalDependency } page={ pageD } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [25, 50, 100] } onPageChange={ ( _, p ) => setPageD( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

      { snackbar }
    </Box>
  );
};

export default Job;
