import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchCartographerList } from '../store/cartographerSlice';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';

const Cartographer: React.FC = () =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, loading, error } = useSelector( ( s: RootState ) => s.cartographer );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    dispatch( fetchCartographerList() );
  }, [authenticated, dispatch] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  return (
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
  );
};

export default Cartographer;
