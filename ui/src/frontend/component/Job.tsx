import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { contractor } from '../store';
import { fetchFoundationJobList, fetchStructureJobList, fetchDependencyJobList, fetchJobDetail, pauseJob, resumeJob, resetJob, rollbackJob } from '../store/jobsSlice';
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
  if ( item[1] === 'Function' && item[2]?.dispatched )
    return <Box key={ idx }><strong>Task Dispatched</strong></Box>;

  if ( item[1] === 'Scope' )
  {
    if ( item[2] === null )
      return <Box key={ idx }>{ item[0].toLocaleString( undefined, { minimumFractionDigits: 2 } ) }%</Box>;

    if ( item[2]?.time_remaining )
    {
      if ( item[2].time_remaining[0] === '-' )
        return <Box key={ idx } sx={{ bgcolor: 'orange' }}><strong>{ item[2].description }</strong> { item[0].toLocaleString( undefined, { minimumFractionDigits: 2 } ) }% Elapsed:&nbsp;{ item[2].time_elapsed } Remaining:&nbsp;{ item[2].time_remaining }</Box>;

      return <Box key={ idx }><strong>{ item[2].description }</strong> { item[0].toLocaleString( undefined, { minimumFractionDigits: 2 } ) }% Elapsed:&nbsp;{ item[2].time_elapsed } Remaining:&nbsp;{ item[2].time_remaining }</Box>;
    }

    return <Box key={ idx }><strong>{ item[2].description }</strong> { item[0].toLocaleString( undefined, { minimumFractionDigits: 2 } ) }% Elapsed:&nbsp;{ item[2].time_elapsed }</Box>;
  }

  return null;
};

const Job: React.FC<Props> = ( { id, jobType, site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { listFoundation, listStructure, listDependency, detail, loading, error } = useSelector( ( s: RootState ) => s.jobs );
  const [snackMessage, setSnackMessage] = useState( '' );
  const [snackSeverity, setSnackSeverity] = useState<'success' | 'error'>( 'success' );
  const [snackOpen, setSnackOpen] = useState( false );
  const [pageF, setPageF] = useState( 0 );
  const [pageS, setPageS] = useState( 0 );
  const [pageD, setPageD] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( 25 );
  const actionGenRef = useRef( 0 );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchJobDetail( { id, jobType: jobType ?? '' } ) );
    else
    {
      dispatch( fetchFoundationJobList( site ?? '' ) );
      dispatch( fetchStructureJobList( site ?? '' ) );
      dispatch( fetchDependencyJobList( site ?? '' ) );
    }
  }, [authenticated, dispatch, id, jobType, site] );

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
                <TableRow><TableCell variant="head">State</TableCell><TableCell>{ detail.job.state }</TableCell></TableRow>
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

  const rowsF = listFoundation || [];
  const rowsS = listStructure || [];
  const rowsD = listDependency || [];

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
          { rowsF.slice( pageF * rowsPerPage, pageF * rowsPerPage + rowsPerPage ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/f/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/foundation/' + item.foundation }>{ item.foundation }</Link></TableCell>
              <TableCell>{ item.message }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ rowsF.length } page={ pageF } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [10, 25, 50, 100] } onPageChange={ ( _, p ) => setPageF( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

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
          { rowsS.slice( pageS * rowsPerPage, pageS * rowsPerPage + rowsPerPage ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/s/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/structure/' + item.structure }>{ item.structure }</Link></TableCell>
              <TableCell>{ item.message }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ rowsS.length } page={ pageS } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [10, 25, 50, 100] } onPageChange={ ( _, p ) => setPageS( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

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
          { rowsD.slice( pageD * rowsPerPage, pageD * rowsPerPage + rowsPerPage ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell align="right"><Link component={ RouterLink } to={ '/job/d/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.script }</TableCell>
              <TableCell>{ item.dependency }</TableCell>
              <TableCell>{ item.message }<br/>{ item.status.map( ( s: any, idx: number ) => renderStatus( s, idx ) ) }</TableCell>
              <TableCell><Chip size="small" label={ item.state } color={ stateColor( item.state ) } /></TableCell>
              <TableCell><strong>Created:</strong>&nbsp;{ item.created }<br/><strong>Updated:</strong>&nbsp;{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination component="div" count={ rowsD.length } page={ pageD } rowsPerPage={ rowsPerPage } rowsPerPageOptions={ [10, 25, 50, 100] } onPageChange={ ( _, p ) => setPageD( p ) } onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPageF( 0 ); setPageS( 0 ); setPageD( 0 ); } } />

      { snackbar }
    </Box>
  );
};

export default Job;
