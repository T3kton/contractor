import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchJobLogList } from '../store/jobLogSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, CircularProgress, Table, TableBody, TableCell, TableHead, TablePagination, TableRow } from '@mui/material';
import type { RootState, AppDispatch } from '../store';

interface Props {
  site?: string;
}

const JobLog: React.FC<Props> = ( { site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, loading, error } = useSelector( ( s: RootState ) => s.jobLog );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchJobLogList( { site: site ?? '', position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, site, page, rowsPerPage, updateVersion] );

  useEffect( () => { setPage( 0 ); }, [site] );
  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  return (
    <Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Job Id</TableCell>
            <TableCell>Site</TableCell>
            <TableCell>Target Class</TableCell>
            <TableCell>Target Description</TableCell>
            <TableCell>Script Name</TableCell>
            <TableCell>Creator</TableCell>
            <TableCell>Started At</TableCell>
            <TableCell>Finished At</TableCell>
            <TableCell>Canceled By</TableCell>
            <TableCell>Canceled At</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell>{ item.job_id }</TableCell>
              <TableCell>{ item.site }</TableCell>
              <TableCell>{ item.target_class }</TableCell>
              <TableCell>{ item.target_description }</TableCell>
              <TableCell>{ item.script_name }</TableCell>
              <TableCell>{ item.creator }</TableCell>
              <TableCell>{ item.started_at }</TableCell>
              <TableCell>{ item.finished_at }</TableCell>
              <TableCell>{ item.canceled_by }</TableCell>
              <TableCell>{ item.canceled_at }</TableCell>
            </TableRow>
          ) ) }
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={ total }
        page={ page }
        rowsPerPage={ rowsPerPage }
        rowsPerPageOptions={ [25, 50, 100] }
        onPageChange={ ( _, p ) => setPage( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPage( 0 ); } }
      />
    </Box>
  );
};

export default JobLog;
