import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ErrorPanel from './ErrorPanel';
import { fetchPXEList, fetchPXE } from '../store/pxeSlice';
import { Box, CircularProgress, Link, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { RootState, AppDispatch } from '../store';
import { dateStr } from '../lib/utils';

interface Props {
  id?: string;
  site?: string;
}

const PXE: React.FC<Props> = ( { id } ) =>
{
  const dispatch = useDispatch<AppDispatch>();
  const authenticated = useSelector( ( s: RootState ) => s.app.authenticated );
  const { list, detail, loading, error } = useSelector( ( s: RootState ) => s.pxe );

  const fetchData = useCallback( () =>
  {
    if ( !authenticated ) return;
    if ( id !== undefined ) dispatch( fetchPXE( id ) );
    else dispatch( fetchPXEList() );
  }, [authenticated, dispatch, id] );

  useEffect( () => { fetchData(); }, [fetchData] );

  if ( loading ) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if ( error ) return <ErrorPanel error={ error } onRetry={ fetchData } />;

  if ( id !== undefined )
  {
    return (
      <Box>
        <Link component={ RouterLink } to="/pxes">&larr; PXEs</Link>
        <Typography variant="h5" gutterBottom>PXE Detail</Typography>
        { detail !== null &&
          <Table size="small" sx={{ mt: 1 }}>
            <TableBody>
              <TableRow><TableCell variant="head">Name</TableCell><TableCell>{ detail.name }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Boot Script</TableCell><TableCell><pre>{ detail.boot_script }</pre></TableCell></TableRow>
              <TableRow><TableCell variant="head">Template</TableCell><TableCell><pre>{ detail.template }</pre></TableCell></TableRow>
              <TableRow><TableCell variant="head">Created</TableCell><TableCell>{ dateStr( detail.created ) }</TableCell></TableRow>
              <TableRow><TableCell variant="head">Updated</TableCell><TableCell>{ dateStr( detail.updated ) }</TableCell></TableRow>
            </TableBody>
          </Table>
        }
      </Box>
    );
  }

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        { ( list || [] ).map( ( item ) => (
          <TableRow key={ item.name }>
            <TableCell><Link component={ RouterLink } to={ '/pxe/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </TableBody>
    </Table>
  );
};

export default PXE;
