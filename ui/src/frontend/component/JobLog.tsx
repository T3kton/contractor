import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchJobLogList } from '../store/jobLogSlice';
import { Box, CircularProgress, Table, TableBody, TableCell, TableHead, TablePagination, TableRow } from '@mui/material';
import type { RootState, AppDispatch } from '../store';

interface Props {
  site?: string;
}

const JobLog: React.FC<Props> = ( { site } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, loading, error } = useSelector( ( s: RootState ) => s.jobLog );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( 25 );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchJobLogList( site ?? '' ) );
  }, [authenticated, dispatch, site] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  const rows = list || [];

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
          { rows.slice( page * rowsPerPage, page * rowsPerPage + rowsPerPage ).map( ( item ) => (
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
        count={ rows.length }
        page={ page }
        rowsPerPage={ rowsPerPage }
        rowsPerPageOptions={ [10, 25, 50, 100] }
        onPageChange={ ( _, p ) => setPage( p ) }
        onRowsPerPageChange={ ( e ) => { setRowsPerPage( parseInt( e.target.value, 10 ) ); setPage( 0 ); } }
      />
    </Box>
  );
};

export default JobLog;
