import React, { useCallback, useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchCartographerList } from '../store/cartographerSlice';
import { DEFAULT_PAGE_SIZE } from '../store/sliceFactory';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TablePagination, TableRow } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';

const Cartographer: React.FC = () =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const updateVersion = useSelector( ( s: RootState ) => s.app.updateVersion );
  const { list, total, loading, error } = useSelector( ( s: RootState ) => s.cartographer );
  const [page, setPage] = useState( 0 );
  const [rowsPerPage, setRowsPerPage] = useState( DEFAULT_PAGE_SIZE );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchCartographerList( { position: page * rowsPerPage, count: rowsPerPage } ) );
  }, [authenticated, dispatch, page, rowsPerPage, updateVersion] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  return (
    <Box>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Identifier</TableCell>
            <TableCell>Message</TableCell>
            <TableCell>Foundation</TableCell>
            <TableCell>Last Checkin</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          { ( list || [] ).map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell>{ item.identifier }</TableCell>
              <TableCell>{ item.message }</TableCell>
              <TableCell><Link component={ RouterLink } to={ '/foundation/' + item.foundation }>{ item.foundation }</Link></TableCell>
              <TableCell>{ item.last_checkin }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
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

export default Cartographer;
